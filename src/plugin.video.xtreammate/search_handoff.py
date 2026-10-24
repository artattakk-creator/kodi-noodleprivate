"""Explicit Kodi RunScript entry for an already authorized native search."""
import os
import sys

root=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(root,'resources','lib'))

if __name__=='__main__':
    from search_handoff import run
    run(sys.argv[1] if len(sys.argv)>1 else '')
