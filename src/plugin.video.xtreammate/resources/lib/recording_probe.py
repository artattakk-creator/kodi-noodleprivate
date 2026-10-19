"""Explicit read-only executable probe, not a claim of working recordings."""
import shutil
import subprocess


def report():
    binary=next((value for name in ('ffmpeg','/usr/bin/ffmpeg','/usr/local/bin/ffmpeg') if (value:=shutil.which(name))),None)
    lines=['Android-Aufnahmefähigkeit: separate Geräteprüfung',
           'Diese Prüfung installiert nichts und startet keine Aufnahme.']
    if not binary:
        lines.append('FFmpeg: kein ausführbarer Kandidat gefunden.')
    else:
        try:
            result=subprocess.run([binary,'-version'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=2,check=False)
            lines.append('FFmpeg-Versionsprobe: '+('ausführbar' if result.returncode==0 else 'fehlgeschlagen'))
        except (OSError,subprocess.TimeoutExpired): lines.append('FFmpeg-Versionsprobe: fehlgeschlagen / Zeitlimit.')
    lines+=['PVR-Engine / Zuordnung der IPTV-Sender: nicht verifiziert.',
            'Aufnahmeordner separat prüfen; freier Speicher und Provider-Parallelstreams müssen reichen.',
            'Erst eine nachgewiesene kurze Testaufnahme bestätigt die Aufnahmefähigkeit.',
            'EPG-Aufnahmeplanung und Android-Wakeup sind noch nicht implementiert/freigegeben.']
    return '\n'.join(lines)
