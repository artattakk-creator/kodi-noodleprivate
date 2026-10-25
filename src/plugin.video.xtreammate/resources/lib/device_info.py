"""Read-only measured hardware/process/storage; firmware claims are separate."""
import json
import os
import platform
import shutil
import struct
import subprocess
import time


def proc_values(filename,keys):
    result={}
    try:
        with open(filename,encoding='utf-8',errors='replace') as stream:
            for line in stream.read(65536).splitlines():
                key,sep,value=line.partition(':')
                if sep and key.strip() in keys:result[key.strip()]=value.strip()[:160]
    except OSError:pass
    return result


def android_properties():
    result={}
    for name in ('ro.build.version.sdk','ro.build.version.release','ro.build.version.security_patch'):
        try:
            value=subprocess.run(['/system/bin/getprop',name],capture_output=True,timeout=1,check=False,text=True).stdout.strip()[:80]
            if value:result[name]=value
        except (OSError,subprocess.TimeoutExpired):pass
    return result


def filesystem(path):
    try:
        root=path
        while not os.path.isdir(root) and root!=os.path.dirname(root):root=os.path.dirname(root)
        usage=shutil.disk_usage(root)
        return dict(total=usage.total,free=usage.free,used=usage.used)
    except OSError:return dict(code='UNKNOWN')


def texture_inventory(root):
    """Bounded explicit diagnostic, never deletes Kodi cache/Texture DB."""
    count=0;size=0;deadline=time.monotonic()+.25;pending=[root]
    try:
        while pending:
            with os.scandir(pending.pop()) as entries:
                for entry in entries:
                    if count>=5000 or time.monotonic()>deadline:return dict(files=count,bytes=size,partial=True)
                    if entry.is_dir(follow_symlinks=False):pending.append(entry.path)
                    elif entry.is_file(follow_symlinks=False):count+=1;size+=entry.stat(follow_symlinks=False).st_size
        return dict(files=count,bytes=size,partial=False)
    except OSError:return dict(code='UNKNOWN',files=count,bytes=size,partial=True)


def collect():
    import xbmc,xbmcaddon,xbmcvfs
    from utils import addon_data_dir
    from artwork_config import read
    from artwork_backend import active_backend
    from art_storage import capacity
    from service_runtime import memory
    def kib(value):
        try:return int(value.split()[0])*1024
        except (ValueError,AttributeError):return None
    mem=proc_values('/proc/meminfo',('MemTotal','MemAvailable'))
    cpu=proc_values('/proc/cpuinfo',('Hardware','Processor','model name','CPU architecture'))
    properties=android_properties();sdk=properties.get('ro.build.version.sdk')
    expected={'33':'13','34':'14','35':'15','36':'16'}.get(sdk)
    reported=properties.get('ro.build.version.release')
    config=read();storage=active_backend()
    result=dict(kodi=xbmc.getInfoLabel('System.BuildVersion'),addon=xbmcaddon.Addon().getAddonInfo('version'),
                gpu='UNKNOWN unless exposed by a read-only driver interface',process_bits=8*struct.calcsize('P'),machine=platform.machine(),kernel=platform.release(),cpu=cpu,
                ram_total_bytes=kib(mem.get('MemTotal')),ram_available_bytes=kib(mem.get('MemAvailable')),
                process=memory(),android_reported=reported,android_sdk=sdk,android_expected_from_sdk=expected,
                firmware_mismatch=bool(expected and reported and expected!=reported.split('.')[0]),
                advertised_ram_flash='UNVERIFIED; filesystem total is not marketed physical flash',
                artwork_mode=config['mode'],artwork_backend=storage.kind,artwork_availability=storage.availability(),
                userdata_filesystem=filesystem(addon_data_dir()),texture_cache_policy='Kodi-managed; separate from XCMate archive; never cleared here')
    try:result['artwork_capacity']=capacity(backend=storage)
    except OSError:result['artwork_capacity']=dict(code='STORAGE_OFFLINE')
    textures=xbmcvfs.translatePath('special://profile/Thumbnails/')
    result['kodi_texture_cache']=dict(inventory=texture_inventory(textures),filesystem=filesystem(textures))
    return result


def show():
    import xbmcgui
    from artwork_ui import job
    from localization import tr
    while True:
        result=job(lambda cancel,progress:collect())
        if result is None:return
        xbmcgui.Dialog().textviewer(tr(35300),json.dumps(result,ensure_ascii=False,indent=2))
        if not xbmcgui.Dialog().yesno(tr(35300),tr(35301)):return
