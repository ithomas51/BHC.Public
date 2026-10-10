"""Regenerate every deliverable from vector.  python build_all.py [root]   (default root: docs\\brand-assets)"""
import sys
sys.dont_write_bytecode = True
import os
import gen_icons, gen_lockups, gen_3a4d5c, gen_workspace, gen_mobile
from paths import ROOT

GENERATORS = (gen_icons, gen_lockups, gen_3a4d5c, gen_workspace, gen_mobile)


def build(root=ROOT):
    for g in GENERATORS:
        g.build(root)
        print('built', g.__name__, '->', root)


if __name__ == '__main__':
    build(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
