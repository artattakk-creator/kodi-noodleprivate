"""Fresh native picker: real host capacity, synthetic provider/TLS only.

Low-space injections belong to the separate .90 retention job. This fresh
profile retains the production reserve and uses the actual writable volume.
"""
from pathlib import Path
base90=Path('/base_fixture84.py').read_text(encoding='utf-8')
assert base90.count('usage.fault84=True;shutil.disk_usage=usage')==1
base90=base90.replace('usage.fault84=True;shutil.disk_usage=usage','usage.fault84=True  # no capacity injection in the fresh picker profile')
base90='\n'.join(line for line in base90.splitlines() if line.strip()!="if __name__=='__main__':run()")
exec(compile(base90,'/base_fixture84.py','exec'),globals())
if __name__=='__main__':run()
