"""Deterministic original gray-blue transparent guide border, no old asset edit."""
import binascii,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build():
 width,height=128,54
 def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',binascii.crc32(kind+data)&0xffffffff)
 rows=b''.join(b'\0'+b''.join(bytes((58,75,91,255)) if x<4 or x>=width-4 or y<4 or y>=height-4 else b'\0\0\0\0' for x in range(width)) for y in range(height))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b'')
if __name__=='__main__':(ROOT/'src/plugin.video.xtreammate/resources/media/guide_focus80.png').write_bytes(build())
