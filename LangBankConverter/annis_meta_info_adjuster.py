# This script performs some basic renaming of complexity meta information for the LangBank
# project. 
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

import sys
import os
import shutil
import manager.system_manager as sm


class MetaStructurer:

    @staticmethod
    def rec_rename_meta_info(in_dir, out_dir):
        new_data = sm.FileHandler.rec_rval_process(in_dir, '.meta', lambda x: MetaStructurer.rename_meta_info(x))
        sm.FileHandler.write_to_dir(new_data, out_dir)
        print('Done.')

    @staticmethod
    def rename_meta_info(in_file, remove_redundant=True):
        rval = ''
        instr = open(in_file, 'r')
        for line in instr.readlines():
            l = line.strip().lower()
            prefix = ''
            if l.startswith('wor_wo_'):
                prefix = 'lex'
            elif l.startswith('wor_mo_'):
                prefix = 'mor'
            elif l.startswith('sen_np') or l.startswith('sen_vp') or l.startswith('sen_xp'):
                prefix = 'phr'
            elif l.startswith('sen'):
                # ignore all syntactic sentence features that were normalized by t-unit or (finite) clause
                if remove_redundant and (l.startswith('sen_tu') or l.startswith('sen_fc') or l.startswith('sen_cl')) and not '_dlt_' in l:
                    continue
                prefix = 'sen'
            elif l.startswith('tex'):
                prefix = 'coh'
            rval += 'cfeat\\:\\:{}_{}\n'.format(prefix, line.strip()[line.strip().rfind('_')+1:])  # namespace\:\:name=value
        instr.close()
        return rval


if __name__ == '__main__':

    rsrc_dir = os.path.sep.join(['..', 'Lib', 'rsrc'])

    if len(sys.argv) < 3:
        print('Wrong call. Run\n> python3 annis_meta_info_adjuster.py IN_DIR OUT_DIR')
        sys.exit(0)
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    MetaStructurer.rec_rename_meta_info(in_dir, out_dir)