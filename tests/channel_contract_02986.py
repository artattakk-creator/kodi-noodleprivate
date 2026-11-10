""".86 is review-only. All committed .85 channels remain byte-exact main."""
import hashlib
import subprocess
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
BASE='c6124922d067361e37db4dd325710ea89a96002e'
def approved(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def verify(path,committed=False):
    from channel_contract_02987 import verify as verify87
    return verify87(path,committed)
