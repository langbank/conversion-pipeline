# This script reduces Ridges data in excel format if the are too large to be processed.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

import sys
import manager.system_manager as sm


# TODO rewrite with openpyxl or discard

def get_relevant_column_content(file, relevant_columns, delim=','):
    rval = ''
    header = True
    idx = []
    instr = open(file, 'r')
    for line in instr.readlines():
        row = line.split(delim)
        if header:
            header = False
            counter = -1
            for cell in row:
                counter += 1
                # add column ids of header cells that are in set of relevant columns
                if cell.strip() in relevant_columns:
                    idx.append(counter)
                # stop when all relevant columns have been found
                if len(idx) == len(relevant_columns):
                    break
            continue
        rval += delim.join([row[i] for i in idx])+'\n'
    instr.close()
    return rval


if __name__ == '__main__':

    n_args = 3
    if len(sys.argv) < n_args:
        print('Wrong Call!')  # TODO more verbose
        sys.exit(0)

    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    # Get all relevant files

    # Retrieve data from all relevant files including only relevant columns
    relevant_columns = ['dipl', 'clean', 'norm', 'sentence_end', 'note', 'head']
    reduced_data = sm.FileHandler.rec_rval_process(in_dir, '.xlsx', lambda x: get_relevant_column_content(x, relevant_columns))
    sm.FileHandler.write_to_dir(reduced_data, out_dir)