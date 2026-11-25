"""Build GS Media Setup 0.5.30 from the exact released 0.5.29 ZIP.

Only Pilot/NeoDark3 files are generated. No access tokens, device data, or
changes to XCMate itself. Run from the repository root with Python 3.11.
"""
import ast
import hashlib
import io
import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path("online-test")
OLD = "0.5.29"
NEW = "0.5.30"
XC = "0.1.29.102"
OLD_HASH = "f69e5c5e78381fb89bcb51447b4907f7b9c18adf200cc2730246a2950ab2c0b4"
XC_HASH = "2c079e6c48ee027370b2a971b2ad942f12af19da0a2536ebed5e3563cdcd27ae"
P = "script.gsmedia.setup/"
BRIDGE = "script.gsmedia.upgrade.plugin.video.xtreammate"
BRIDGE_VERSION = "0.1.0"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def read_zip(path, expected=None):
    data = path.read_bytes()
    if expected:
        require(sha(data) == expected, "HASH_MISMATCH: " + str(path))
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        require(z.testzip() is None, "BAD_CRC: " + str(path))
        result = {}
        for entry in z.infolist():
            if entry.is_dir():
                continue
            name = entry.filename
            require(name not in result and not name.startswith("/") and
                    "\\" not in name and ".." not in Path(name).parts,
                    "UNSAFE_ZIP_ENTRY: " + name)
            result[name] = z.read(entry)
        return result

def make_zip(files):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compresslevel=8)
    payload = out.getvalue()
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        require(z.testzip() is None and set(z.namelist()) == set(files), "BAD_OUTPUT")
        require(all(z.read(name) == data for name, data in files.items()), "OUTPUT_BYTE_MISMATCH")
    return payload

def write_package(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    path.with_name(path.name + ".sha256").write_text(sha(payload) + "  " + path.name + "\n", encoding="utf-8")

def replace_once(s, before, after):
    require(s.count(before) == 1, "UNEXPECTED_PATCH_CONTEXT: " + before[:100])
    return s.replace(before, after, 1)

def build():
    source = ROOT / ("script.gsmedia.setup-" + OLD + ".zip")
    xc_path = ROOT / "plugin.video.xtreammate" / ("plugin.video.xtreammate-" + XC + ".zip")
    xc = read_zip(xc_path, XC_HASH)
    xprefix = "plugin.video.xtreammate/"
    require(ET.fromstring(xc[xprefix+"addon.xml"]).get("version") == XC, "XCMATE_VERSION")
    require(xprefix+"resources/lib/epg_agent_public.py" in xc, "NO_PUBLIC_AGENT")
    require(not any("/resources/private/" in name and "token" in name.lower() for name in xc), "PRIVATE_TOKEN_MEMBER")
    settings = {el.get("id"): el for el in ET.fromstring(xc[xprefix+"resources/settings.xml"]).iter("setting")}
    for key, value in (("epg_agent_enabled", "true"), ("epg_agent_country_de", "true"),
                       ("epg_agent_private", "false")):
        require(settings[key].get("default") == value, "WRONG_AGENT_DEFAULT: "+key)
    require("action=epg_agent100" in settings["epg_agent_status"].get("action", ""), "NO_EPG_ROUTE")
    original = read_zip(source, OLD_HASH)
    files = dict(original)
    def patch(name, before, after):
        path = P + name
        files[path] = replace_once(files[path].decode("utf-8"), before, after).encode("utf-8")
    patch("addon.xml", 'version="0.5.29"', 'version="0.5.30"')
    patch("addon.xml", "<news>Issue #496: Begrenzt wiederholbarer Kodi-Katalogscan und sicheres Fortsetzen der vollständigen 48-Komponenten-Einrichtung.</news>",
          "<news>0.5.30: XCMate ab 0.1.29.102 aus Pilot, öffentlicher EPG-Agent ohne GitHub-Token, bestehende Einstellungen und 48 Komponenten erhalten. Geräteabnahme offen.</news>")
    patch("resources/lib/setup_auto50.py", 'minimum="0.1.29.101"', 'minimum="0.1.29.102"')
    patch("resources/lib/setup_auto_ui50.py", 'TITLE = "GS Media Setup 0.5.29"', 'TITLE = "GS Media Setup 0.5.30"')
    patch("resources/lib/setup_options27.py", '"XCMate EPG Agent – noch nicht verfügbar"', '"XCMate EPG Agent – öffentlich (ohne GitHub-Token)"')
    patch("resources/lib/setup_options27.py",
          '    if choice == 3:\n        dialog.ok(title, "XCMate EPG Agent kann später in XCMate → Einstellungen → EPG "\n                         "eingerichtet werden. Der Anbieter-EPG bleibt aktiv.")\n        return\n    if choice not in (0, 1, 2):',
          '    if choice not in (0, 1, 2, 3):')
    patch("resources/lib/setup_options27.py",
          '        if choice == 0:\n',
          '        if choice == 3:\n            if not (modules / "epg_agent_public.py").is_file():\n                dialog.ok(title, "Öffentlicher EPG-Agent benötigt XCMate ab 0.1.29.102.")\n                return\n            dialog.ok(title, "Öffentlicher EPG-Agent: Bei Neuinstallation ist Deutschland voreingestellt. Kein GitHub-Token erforderlich. Vorhandene Einstellungen bleiben erhalten. Der Anbieter-EPG bleibt unabhängig aktiv.")\n            xbmc.executebuiltin("RunPlugin(plugin://plugin.video.xtreammate/?action=epg_agent100)")\n        elif choice == 0:\n')
    files[P+"README.md"] = (
        "# GS Media Setup 0.5.30 – Pilot / NeoDark3 Test\n\n"
        "Basis: veröffentlichtes 0.5.29-Paket. XCMate ab 0.1.29.102 aus Pilot. "
        "Öffentlicher EPG-Agent ohne GitHub-Token; vorhandene Einstellungen werden nicht überschrieben. "
        "48 Komponenten, TMDB-Option, BINGIE und Branding bleiben unverändert. "
        "Physische Android-/LG-webOS-Abnahme offen.\n\n"
        "## Historische Dokumentation der Basis (unverändert)\n\n"
    ).encode() + original[P+"README.md"]
    changed = {name for name in files if files[name] != original[name]}
    require(changed == {P+x for x in ("addon.xml","README.md","resources/lib/setup_auto50.py",
                    "resources/lib/setup_auto_ui50.py","resources/lib/setup_options27.py")}, "PATCH_SCOPE")
    require(set(files) == set(original), "MEMBER_SCOPE")
    for name, data in files.items():
        if name.endswith(".py"):
            ast.parse(data.decode("utf-8"), filename=name)
    require(ET.fromstring(files[P+"addon.xml"]).get("version") == NEW, "INSTALLER_VERSION")

    # Actual pure planner from both complete ZIPs, isolated imports, no Kodi needed.
    def planner(data):
        module = ast.parse(data[P+"resources/lib/setup_auto50.py"].decode())
        return module
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for name, data in files.items():
            dest = base/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        sys.path.insert(0, str(base/P/"resources/lib"))
        try:
            import setup_auto50 as auto
            import setup_compat27 as compat
            old_tree = planner(original)
            old_function = next(n for n in old_tree.body if isinstance(n,ast.FunctionDef) and n.name=="rows")
            env = dict(vars(auto))
            exec(compile(ast.Module(body=[old_function],type_ignores=[]),"<old-rows>","exec"),env)
            old_rows = list(env["rows"]())
            new_rows = list(auto.rows())
            require(len(old_rows)==len(new_rows)==48, "COMPONENT_COUNT")
            differences = [(a,b) for a,b in zip(old_rows,new_rows) if a!=b]
            require(len(differences)==1 and differences[0][0]["id"]=="plugin.video.xtreammate"
                    and differences[0][0]["minimum"]=="0.1.29.101"
                    and differences[0][1]==dict(differences[0][0],minimum=XC), "PLAN_DIFF")
            require(auto.upgrade_bridge_for("plugin.video.xtreammate","repository.gsmedia.pilot",XC)==BRIDGE, "BRIDGE_LOOKUP")
            require(next(r for r in compat.manifest() if r["id"]=="plugin.video.xtreammate")["minimum"]==XC, "FINISH_GATE")
            require(not auto.installed({"code":"READY","addons":{"plugin.video.xtreammate":{"version":"0.1.29.101","enabled":True}}},"plugin.video.xtreammate",XC), "OLD_VERSION_ACCEPTED")
            require(auto.installed({"code":"READY","addons":{"plugin.video.xtreammate":{"version":XC,"enabled":True}}},"plugin.video.xtreammate",XC), "NEW_VERSION_REJECTED")
            require(auto.validate(auto.new_state())["schema"]==2, "JOURNAL_SCHEMA")
            # Run actual _native_pilot_bridge function with its injected lookup.
            omega=ast.parse(files[P+"resources/lib/setup_omega26.py"].decode())
            fn=next(n for n in omega.body if isinstance(n,ast.FunctionDef) and n.name=="_native_pilot_bridge")
            ctx={}
            exec(compile(ast.Module(body=[fn],type_ignores=[]),"<bridge-selector>","exec"),ctx)
            select=ctx["_native_pilot_bridge"]
            for code in ("INSTALL_ADDON","INSTALL_UPGRADE"):
                step={"id":"plugin.video.xtreammate","source":"repository.gsmedia.pilot","minimum":XC}
                require(bool(select(code,step,auto.upgrade_bridge_for)), "BRIDGE_NOT_SELECTED_"+code)
        finally:
            sys.path.pop(0)

    # Reuse existing inert Pilot bridge format. Exact new dependency minimum.
    template="script.gsmedia.upgrade.plugin.audio.m3sr2019"
    old_bridge=read_zip(ROOT/template/(template+"-0.1.0.zip"))
    bridge_xml=ET.fromstring(old_bridge[template+"/addon.xml"])
    bridge_xml.set("id",BRIDGE)
    bridge_xml.set("name","XCMate Dependency Upgrade - plugin.video.xtreammate")
    for imp in bridge_xml.findall("./requires/import"):
        if imp.get("addon")=="plugin.audio.m3sr2019":
            imp.set("addon","plugin.video.xtreammate");imp.set("version",XC)
    for desc in bridge_xml.findall("./extension/description"):
        desc.text="First-party inert resolver: asks Kodi's native add-on dependency manager to select the original plugin.video.xtreammate at minimum "+XC+". No user data modified."
    bridge_fragment=ET.tostring(bridge_xml,encoding="unicode")
    bridge_files={BRIDGE+"/addon.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'+bridge_fragment+"\n").encode(),
                  BRIDGE+"/default.py":old_bridge[template+"/default.py"]}
    require(bridge_xml.find("./requires/import[@addon='plugin.video.xtreammate']").get("version")==XC,"BRIDGE_DEPENDENCY")
    ast.parse(bridge_files[BRIDGE+"/default.py"].decode())
    bridge_payload=make_zip(bridge_files)

    catalog=ROOT/"addons.xml"
    xml=catalog.read_text(encoding="utf-8")
    root=ET.fromstring(xml)
    require(root.find("./addon[@id='plugin.video.xtreammate']").get("version")==XC,"PILOT_NOT_102")
    require(root.find("./addon[@id='"+BRIDGE+"']") is None,"BRIDGE_ALREADY_EXISTS")
    match=re.search(r'<addon id="script\.gsmedia\.setup".*?</addon>',xml,re.S)
    require(bool(match),"SETUP_CATALOG_MISSING")
    fragment=replace_once(match.group(),'version="0.5.29"','version="0.5.30"')
    xml=xml[:match.start()]+fragment+xml[match.end():]
    xml=replace_once(xml,"</addons>",bridge_fragment+"</addons>")
    updated=ET.fromstring(xml)
    require(updated.find("./addon[@id='script.gsmedia.setup']").get("version")==NEW,"CATALOG_SETUP_VERSION")
    require(updated.find("./addon[@id='"+BRIDGE+"']/requires/import[@addon='plugin.video.xtreammate']").get("version")==XC,"CATALOG_BRIDGE_VERSION")
    # Other catalog entries stay semantically identical.
    for before in root.findall("addon"):
        if before.get("id")=="script.gsmedia.setup":continue
        require(ET.tostring(before)==ET.tostring(updated.find("./addon[@id='"+before.get("id")+"']")),"OTHER_CATALOG_ENTRY_CHANGED")

    payload=make_zip(files)
    name="script.gsmedia.setup-"+NEW+".zip"
    for path in (ROOT/name,ROOT/"script.gsmedia.setup"/name):
        write_package(path,payload)
    write_package(ROOT/BRIDGE/(BRIDGE+"-"+BRIDGE_VERSION+".zip"),bridge_payload)
    catalog.write_text(xml,encoding="utf-8")
    (ROOT/"addons.xml.md5").write_text(hashlib.md5(catalog.read_bytes()).hexdigest()+"\n",encoding="ascii")
    index=ROOT/"index.html"
    html=index.read_text(encoding="utf-8")
    needle='<tr><td><a href="script.gsmedia.setup-0.5.29.zip">'
    line='<tr><td><a href="'+name+'">'+name+'</a></td><td><strong>2a. GS Media Installer 0.5.30 – XCMate 0.1.29.102</strong><br>48 Komponenten, öffentlicher EPG-Agent ohne GitHub-Token, BINGIE und Space Blue. Android/LG-webOS-Geräteabnahme offen. <a href="'+name+'.sha256">SHA-256</a>.</td></tr>\n'
    index.write_text(replace_once(html,needle,line+needle),encoding="utf-8")
    manifest=ROOT/"manifest.json"
    j=json.loads(manifest.read_text(encoding="utf-8"))
    j["installer_0530"]={"version":NEW,"channel":"PILOT_NeoDark3","base_version":OLD,
        "package_count":48,"xcmate_minimum":XC,"xcmate_sha256":XC_HASH,"xcmate_source":"repository.gsmedia.pilot",
        "public_epg":True,"android_test":"NOT_TESTED","lg_webos_test":"NOT_TESTED",
        "installer_sha256":sha(payload),"bytes":len(payload),"upgrade_bridge":BRIDGE,
        "bridge_sha256":sha(bridge_payload),"changed_members":sorted(changed)}
    j["upgrade_bridges"]=sorted(set(j["upgrade_bridges"])|{BRIDGE})
    manifest.write_text(json.dumps(j,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(j["installer_0530"],ensure_ascii=False,indent=2))
    print("PASS: exact 0.5.29 source + 0.1.29.102 ZIP; 48 components unchanged except XCMate minimum; Python AST, CRC, package byte readback, planner, bridge, journal schema, EPG defaults, catalog. Physical devices NOT_TESTED.")

if __name__=="__main__":
    build()
