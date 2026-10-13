import sys
import os


ADDON_PATH = os.path.dirname(os.path.abspath(__file__))
LIB_PATH   = os.path.join(ADDON_PATH, 'resources', 'lib')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

from main import Router

if __name__ == '__main__':
    Router(sys.argv).dispatch()
