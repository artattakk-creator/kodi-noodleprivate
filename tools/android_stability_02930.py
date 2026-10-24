"""Four-hour ADB companion: numeric dumpsys samples only, never raw Kodi logs.

The in-addon Stability menu records portal/worker metrics and actual Python
pointer width. This optional host tool samples the whole Kodi OS process.
"""
import argparse,json,re,subprocess,time
from pathlib import Path


def parse_memory(text):
    def number(pattern):
        found=re.search(pattern,text,re.M)
        return int(found[1]) if found else None
    return dict(pss_kib=number(r'TOTAL PSS:\s*(\d+)') or number(r'^\s*TOTAL\s+(\d+)'),rss_kib=number(r'TOTAL RSS:\s*(\d+)'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hours',type=float,default=4);parser.add_argument('--interval',type=int,default=60)
    parser.add_argument('--adb',default='adb');parser.add_argument('--serial');parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not .01<=args.hours<=8 or not 5<=args.interval<=300:parser.error('hours .01..8; interval 5..300')
    command=[args.adb]+(['-s',args.serial] if args.serial else [])
    deadline=time.monotonic()+args.hours*3600;started=time.monotonic()
    # Exclusive creation protects an existing report. Do not save raw dumpsys,
    # serial, hostnames, process maps, media names, accounts or logcat output.
    with args.output.open('x',encoding='utf-8') as report:
        while time.monotonic()<deadline:
            status='UNAVAILABLE';values=dict(pss_kib=None,rss_kib=None)
            try:
                result=subprocess.run(command+['shell','dumpsys','meminfo','org.xbmc.kodi'],capture_output=True,timeout=15,text=True)
                if result.returncode==0:
                    values=parse_memory(result.stdout[:4*1024*1024]);status='COLLECTED' if values['pss_kib'] is not None else 'UNAVAILABLE'
            except (OSError,subprocess.TimeoutExpired):pass
            report.write(json.dumps(dict(elapsed_s=int(time.monotonic()-started),status=status,scope='WHOLE_KODI_PROCESS',**values))+'\n');report.flush()
            time.sleep(min(args.interval,max(0,deadline-time.monotonic())))
    print('COLLECTED; actual Android/IR/long-run acceptance must be recorded separately.')


if __name__=='__main__':main()
