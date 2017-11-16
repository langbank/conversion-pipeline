# This script facilitates some simple LangBank specific tree formatting operations.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

import sys
import manager.format_manager as fm
import manager.system_manager as sm


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Wrong call. Run\n> python3 format_manager.py IN_DIR OUT_DIR')
        sys.exit(0)
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    new_data = sm.FileHandler.rec_rval_process(in_dir, '.ptb', lambda x: fm.PTBFormatter.get_lb_tred_format(x))
    # tmp
    for key in new_data.keys():
        cur_text = []
        for line in new_data[key]:
            cur_text.append(line.replace('.0', ''))#.replace('-LRB-', '-').replace('-RRB-', '-'))
        new_data[key] = cur_text
    sm.FileHandler.write_to_dir(new_data, out_dir)

    new_data = sm.FileHandler.rec_rval_process(in_dir, '.conll', lambda x: fm.CONLLFormatter.get_lb_tred_format(x))
    # tmp
    for key in new_data.keys():
        cur_text = []
        for line in new_data[key]:
            cur_text.append(line.replace('.0', ''))#.replace('-LRB-', '(').replace('-RRB-', ')'))
        new_data[key] = cur_text
    sm.FileHandler.write_to_dir(new_data, out_dir)

    print('Done.')