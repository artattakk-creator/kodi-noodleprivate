"""Reproducible tiny PNG controls owned by XCMate, no skin/font dependency."""
from pathlib import Path
import struct,zlib
ROOT=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/media'
def png(name,pixel,size=32):
    def chunk(tag,data):return struct.pack('!I',len(data))+tag+data+struct.pack('!I',zlib.crc32(tag+data)&0xffffffff)
    raw=b''.join(b'\0'+b''.join(bytes(pixel(x,y)) for x in range(size)) for y in range(size))
    ROOT.joinpath(name+'.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',size,size,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
def main():
    for name,color in [('setup_focus',(0,188,212,255)),('setup_normal',(31,51,71,255)),('setup_selected',(22,78,91,255))]:png(name,lambda x,y,c=color:c)
    for checked in (False,True):
        def pixel(x,y):
            border=(3<=x<=28 and 3<=y<=28 and (x<6 or x>25 or y<6 or y>25))
            tick=checked and ((8<=x<=15 and abs(y-(x+6))<=2) or (14<=x<=25 and abs(y-(34-x))<=2))
            return (255,255,255,255) if border or tick else (6,24,32,255) if 6<=x<=25 and 6<=y<=25 else (0,0,0,0)
        png('setup_checked' if checked else 'setup_unchecked',pixel)
if __name__=='__main__':main()
