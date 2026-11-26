"""Native Agent controls and status backed by the service's observed receipts."""
import concurrent.futures
import time

import xbmcgui

from epg_agent100 import enabled, pending_request, profile, publish_variant, request_check, state, use_private
from epg_agent_github import DeliveryError
from epg_agent_hub5 import DEFAULT_PROFILES, save_selection, selection
from localization import tr
from owner_dispatch import OwnerDispatch, native_init

LABELS = {
    "CURRENT": 39104,
    "CHECKING": 39105,
    "IMPORTING": 39105,
    "PRIVATE_ENDPOINT_NETWORK_ERROR": 39106,
    "PRIVATE_ENDPOINT_TEMPORARILY_UNAVAILABLE": 39106,
    "PRIVATE_PENDING": 39109,
    "PUBLIC_PENDING": 39125,
    "PUBLIC_ENDPOINT_NETWORK_ERROR": 39106,
    "NO_PROFILE_SELECTED": 39111,
    "AUTH_NOT_PROVISIONED": 39110,
    "IMPORT_PENDING": 39111,
}
NAMES = {"all": "Gesamt-EPG (ALL)", "de": "Deutschland (DE)", "at": "Österreich (AT)",
         "en": "Englisch (EN)", "es": "Spanisch (ES)", "pl": "Polnisch (PL)",
         "fr": "Französisch (FR)", "it": "Italienisch (IT)",
         "tr": "Türkisch (TR)", "ar": "Arabisch (AR)"}
DELIVERY = {"manifest": "Manifest prüfen", "download": "EPG-Datei herunterladen",
            "validate": "Dateigröße, SHA-256 und XMLTV prüfen"}
IMPORT = {"QUEUED": "Import eingereiht", "WAIT_CATALOG": "Lokalen Katalog abwarten",
          "PARSE": "XMLTV einlesen", "MATCHING": "Sender zuordnen",
          "STAGING": "Import vorbereiten", "COMMIT": "EPG in SQLite speichern",
          "READBACK": "SQLite-Readback prüfen", "CLEANUP": "Import abschließen"}
BUSY = {"CHECKING", "IMPORTING"}


def _when(value):
    return time.strftime("%d.%m.%Y %H:%M", time.localtime(value)) if value else "–"


def _number(value):
    return f"{value:,}".replace(",", ".") if type(value) is int else "–"


def _status(receipt, active):
    if not active:
        return tr(39108)
    code = receipt.get("code")
    return tr(LABELS.get(code, 39107)) if code else tr(39120)


def short_status():
    return _status(state(), enabled())


def _phase(receipt, job):
    if receipt.get("code") == "CHECKING":
        return DELIVERY.get(receipt.get("delivery_phase"), DELIVERY["manifest"])
    if receipt.get("code") == "IMPORTING":
        agent = job.get("sources", {}).get("agent", {})
        phase = agent.get("phase") if job.get("state") == "RUNNING" else None
        return IMPORT.get(phase, "Import wird vorbereitet")
    return ""


def _detail_lines(receipt, selected, current, variant, active, job):
    code = receipt.get("code", "")
    phase = _phase(receipt, job) if active else ""
    lines = [
        phase or _status(receipt, active),
        f"Letzter Check  {_when(receipt.get('last_checked'))}",
        f"Letzter bestätigter Check  {_when(receipt.get('last_successful_check'))}",
        f"{tr(39113)}  {_when(receipt.get('next_check'))}",
        f"Letzter verifizierter Import  {_when(selected.get('last_success'))}",
        f"Auswahl  {' + '.join(p.upper() for p in current) or '–'} · {variant}",
        f"Revision  {str(receipt.get('manifest_revision') or '–')[:22]}",
    ]
    if phase and code == "CHECKING" and receipt.get("download_total"):
        lines.insert(1, "Download  " + _number(receipt.get("download_bytes")) +
                     " / " + _number(receipt["download_total"]) + " Bytes")
    if receipt.get("channels"):
        lines.extend((
            f"Feed  {_number(receipt['channels'])} Sender · {_number(receipt.get('programmes'))} Sendungen",
            f"Bildreferenzen im Feed  {_number(receipt.get('artwork_records'))}",
        ))
    if selected.get("verified"):
        lines.extend((
            f"Zuordnung  {_number(selected.get('matched'))} Streams · "
            f"{_number(selected.get('mapped_channels'))} Sender",
            f"Programme  {_number(selected.get('read'))} gelesen · "
            f"{_number(selected.get('committed'))} gespeichert · "
            f"{_number(selected.get('verified'))} geprüft",
            f"LastGood  {str(selected.get('generation') or '–')[:16]}",
        ))
    if any(key in selected for key in ("unmapped_channels", "ambiguous_streams", "unmatched_streams")):
        lines.append(f"Offen  {_number(selected.get('unmapped_channels'))} Feed-Sender · "
                     f"{_number(selected.get('ambiguous_streams'))} mehrdeutige / "
                     f"{_number(selected.get('unmatched_streams'))} Streams ohne Treffer")
    if selected.get("verified_first") or selected.get("verified_last"):
        lines.append(f"Zeitraum  {_when(selected.get('verified_first'))} – "
                     f"{_when(selected.get('verified_last'))}")
    images = receipt.get("image_counts", {})
    if images:
        lines.extend(("Bilder  Poster / Hintergrund / Still / Senderlogo / Programm-Icon",
                      "            " + " / ".join(_number(images.get(key, 0)) for key in
                      ("poster", "backdrop", "still", "channel_logo", "programme_icon"))))
    http = receipt.get("remote_http_status")
    if type(http) is int:
        subject = "EPG-Datei" if receipt.get("remote_phase") == "asset" else "Manifest"
        lines.append(f"{subject} · HTTP {http}")
    reason = receipt.get("remote_reason")
    codes = " · ".join(dict.fromkeys(filter(None, (code, reason, selected.get("code")))))
    if codes:
        lines.append(codes)
    return lines


def details(portal):
    receipt = state()
    pid = str((portal or {}).get("id", ""))
    try:
        current, variant = selection(profile(), public=not use_private())
    except DeliveryError as exc:
        return exc.code
    from epg_jobs94 import read

    return "\n".join(_detail_lines(receipt, receipt.get("portals", {}).get(pid, {}),
                                   current, variant, enabled(), read(pid)))


def _toggle(current, option):
    if option in current:
        return tuple(key for key in current if key != option)
    if option == "all":
        return ("all",)
    return tuple(key for key in current if key != "all") + (option,)


class AgentSettings(OwnerDispatch, xbmcgui.WindowXMLDialog):
    _native_surface = "dialog"
    _window_view = "AGENT"

    def configure(self, portal):
        self._configure_owner()
        self.portal = portal or {}
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._closed = False
        self._generation = 0
        self._next_poll = 0
        self._request_stamp = 0
        self._request_expires = 0
        self._editing = False
        self.configuration = None
        self.receipt = {}
        self.actions = []
        self._rows = None
        self._status_text = None
        self.next_action = None

    @native_init
    def onInit(self):
        self._request_status()
        self.setFocusId(200)

    def _load(self):
        from artwork_sources96 import enabled as research_enabled
        from epg_jobs94 import read
        from media_sources43 import SourceError

        area = profile()
        active, private = enabled(), use_private()
        receipt = state(area)
        current, variant = selection(area, public=not private)
        if "all" in current:
            current = ("all",)
        transport = "private" if private else "public"
        available = receipt.get("available_profiles") if receipt.get("transport") == transport else None
        choices = tuple(dict.fromkeys((*DEFAULT_PROFILES, *(available or ()), *current)))
        try:
            research = tuple(research_enabled(source) for source in ("tmdb", "tvmaze"))
        except SourceError:
            research = (False, False)
        return ((active, private, current, variant, choices, research), receipt,
                read(str(self.portal.get("id", ""))))

    def _request_status(self):
        if self._editing:
            return
        self._next_poll = time.monotonic() + 1
        self._request(self._load, self._apply)

    def _owner_tick(self):
        if self._pending_future is None and time.monotonic() >= self._next_poll:
            self._request_status()

    def _query_failed(self, exc):
        self._editing = False
        self._next_poll = time.monotonic() + 4
        code = getattr(exc, "code", "")
        code = code if isinstance(code, str) and code.isascii() and code.replace("_", "").isalnum() else "SETTINGS_READBACK_FAILED"
        self.getControl(402).setLabel(code)

    def _apply(self, value):
        self._editing = False
        self.configuration, self.receipt, job = value
        active, private, current, variant, choices, research = self.configuration
        publish_variant(variant)
        rows = [
            (("enable", None), "EPG-Agent", active),
            (("public", None), "Öffentliche Quelle", not private),
            (("private", None), "Private Quelle", private),
            (("images", None), "Sendungsbilder", variant == "artwork"),
        ]
        rows.extend((("profile", key), NAMES.get(key, key.upper()), key in current) for key in choices)
        rows.extend((
            (("research", "tmdb"), "TMDB-Direktrecherche (optional)", research[0]),
            (("research", "tvmaze"), "TVMaze-Direktrecherche (optional)", research[1]),
        ))
        if rows != self._rows:
            control = self.getControl(200)
            index = control.getSelectedPosition()
            previous = self.actions[index] if 0 <= index < len(self.actions) else None
            self.actions = [row[0] for row in rows]
            items = []
            for _, label, flag in rows:
                item = xbmcgui.ListItem(label=label)
                item.setLabel2("An" if flag else "Aus")
                items.append(item)
            control.reset()
            control.addItems(items)
            control.selectItem(self.actions.index(previous) if previous in self.actions else max(0, index))
            self._rows = rows
        selected = self.receipt.get("portals", {}).get(str(self.portal.get("id", "")), {})
        lines = _detail_lines(self.receipt, selected, current, variant, active, job)
        body = "\n".join(lines)
        if body != self._status_text:
            self.getControl(401).setText(body)
            self._status_text = body
        if self._request_stamp and self.receipt.get("request", 0) >= self._request_stamp:
            self._request_stamp = 0
            self.getControl(402).setLabel("")
        if self._request_stamp and time.monotonic() >= self._request_expires:
            self._request_stamp = 0
            self.getControl(402).setLabel("Dienst hat die Anfrage noch nicht bestätigt.")

    def _save(self, action, target):
        from artwork_sources96 import choose
        from epg_agent100 import SETTING
        from settings_guard96 import write

        active, private, current, variant, _choices, research = self.configuration
        if action == "research":
            choose(target, not research[("tmdb", "tvmaze").index(target)])
        elif action in ("enable", "public", "private"):
            if action != "enable" and private == (action == "private"):
                return self._load(), 0
            key = SETTING if action == "enable" else "epg_agent_private"
            value = not active if action == "enable" else action == "private"
            write({key: "true" if value else "false"})
        else:
            if action == "profile":
                current = _toggle(current, target)
            else:
                variant = "standard" if variant == "artwork" else "artwork"
            save_selection(current, variant, profile())
            if selection(profile(), public=not private) != (current, variant):
                raise DeliveryError("HUB5_SELECTION_READBACK_FAILED")
        result = self._load()
        updated = result[0]
        previous = self.configuration
        if previous[3] != updated[3]:
            from programme_refresh63 import request

            publish_variant(updated[3])
            request()
        # A saved change during an import still requires a follow-up check.
        stamp = request_check() if previous[:4] != updated[:4] and updated[0] and updated[2] else 0
        return result, stamp

    def _saved(self, outcome):
        result, stamp = outcome
        previous = self.configuration
        self._apply(result)
        if previous[:4] == self.configuration[:4]:
            self.getControl(402).setLabel("")
            return
        if stamp:
            self._track_request(stamp)
        else:
            self.getControl(402).setLabel("Gespeichert.")

    def _track_request(self, stamp):
        self._request_stamp = stamp
        self._request_expires = time.monotonic() + 80
        self.getControl(402).setLabel("Anfrage an EPG-Dienst gesendet.")

    def onClick(self, control_id):
        self._gui()
        if control_id == 303:
            self.close()
            return
        if control_id == 304:
            self.next_action = "tmdb_access"
            self.close()
            return
        if control_id == 305 and self._status_text:
            xbmcgui.Dialog().textviewer("EPG-Agent · Statusdetails", self._status_text)
            return
        if self.configuration is None or self._editing or self._closed:
            return
        if control_id in (301, 302):
            active, _private, current, *_ = self.configuration
            if not active or not current:
                self.getControl(402).setLabel("EPG-Agent einschalten und ein Profil auswählen.")
            elif self._request_stamp or self.receipt.get("code") in BUSY or pending_request(self.receipt):
                self.getControl(402).setLabel("Eine EPG-Anfrage läuft bereits.")
            else:
                self._track_request(request_check(force=control_id == 302))
        if control_id == 200:
            index = self.getControl(200).getSelectedPosition()
            if 0 <= index < len(self.actions):
                action, target = self.actions[index]
                self._editing = True
                self._request(lambda: self._save(action, target), self._saved)

    def onAction(self, action):
        if action.getId() in (9, 10, 92):
            self.close()

    def close(self):
        self._gui()
        if self._closed:
            return
        self._closed = True
        self._generation += 1
        self._pending_future = self._pending_apply = None
        self._pool.shutdown(wait=False, cancel_futures=True)
        super().close()


def show(portal):
    import xbmcaddon

    root = xbmcaddon.Addon().getAddonInfo("path")
    while True:
        window = AgentSettings("XCMateAgent103.xml", root, "Default", "720p")
        window.configure(portal)
        window.run()
        if window.next_action != "tmdb_access":
            return
        from tmdb_access61 import show as tmdb_access

        tmdb_access()
