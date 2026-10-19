"""Explicit read-only executable probe, not a claim of working recordings."""
from localization import tr
import shutil
import subprocess


def report():
    binary=next((value for name in ('ffmpeg','/usr/bin/ffmpeg','/usr/local/bin/ffmpeg') if (value:=shutil.which(name))),None)
    lines=[tr(32572),
           tr(32573)]
    if not binary:
        lines.append(tr(32574))
    else:
        try:
            result=subprocess.run([binary,'-version'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=2,check=False)
            lines.append(tr(32575)+(tr(32576) if result.returncode==0 else tr(32577)))
        except (OSError,subprocess.TimeoutExpired): lines.append(tr(32578))
    lines+=[tr(32579),
            tr(32580),
            tr(32581),
            tr(32582)]
    return '\n'.join(lines)
