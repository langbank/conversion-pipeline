# This script provides some simple LangBank specific postprocessing functionalities for
# data visualization in ANNIS
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

import sys
import os
import shutil


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Wrong call. Run\n> python3 annis_postprocessor.py TEMPLATE_DIR IN_DIR (OUT_DIR)')
        print('OUT_DIR is optional. If none is given, resolver_vis_map.annis is modified within the input directory.')
        sys.exit(0)
    in_dir = sys.argv[1]
    template_dir = sys.argv[2]
    out_dir = in_dir if len(sys.argv) < 4 else sys.argv[3]

    # A. Adjust resolver_vis_map.annis
    # =================================================================================================================

    # Get corpus name and version
    custom = []
    instr = open(os.path.sep.join([in_dir, 'resolver_vis_map.annis']), 'r')
    for line in instr.readlines():
        l = line.strip().split('\t')
        if len(l) > 1:
            custom = l[:2]  # corpus name, version
            break
    instr.close()

    # Copy template data to annis file
    rval = ''
    instr = open(os.path.sep.join([template_dir, 'resolver_vis_map.annis']), 'r')
    for line in instr.readlines():
        l = line.strip().split('\t')
        rval += '\t'.join(custom+l[2:])+'\n'
    instr.close()

    # Write to file
    outstr = open(os.path.sep.join([out_dir, 'resolver_vis_map.annis']), 'w')
    outstr.write(rval)
    outstr.close()

    # B. Add example queries
    # =================================================================================================================

    # Copy example queries from template_dir
    shutil.copy2(os.path.sep.join([template_dir, 'example_queries.annis']), out_dir)

    # C. Add ExtData visualisation
    # =================================================================================================================

    # Copy fresh ExtData from template_dir
    new_ext_data = os.path.sep.join([out_dir, 'ExtData'])
    if os.path.exists(new_ext_data):
        shutil.rmtree(new_ext_data)
    shutil.copytree(os.path.sep.join([template_dir, 'ExtData']), new_ext_data)

    print('Done.')