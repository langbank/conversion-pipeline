# This script provides some basic system managing functionalities.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

import os


class TempChwd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class FileHandler:

    @staticmethod
    def list_files_in_dir(in_dir, ending):
        """List all files with the given file ending in the given directory and all sub-directories."""
        rval = []
        for root, dirs, files in os.walk(in_dir):
            for name in files:
                if name.endswith(ending) and not name.startswith('.'):
                    rval.append(os.path.join(root, name))
        return rval

    @staticmethod
    def rec_rval_process(in_dir, ending, process):
        """Apply the given process to all files with the given file ending in the directory and all sub-directories."""
        rval = {}
        counter = 0
        for root, dirs, files in os.walk(in_dir):
            for name in files:
                if name.endswith(ending) and not name.startswith('.'):
                    cur = os.path.join(root, name)
                    print('Currently processed file: ' + cur)
                    rval[cur] = process(cur)
                    counter += 1
        print('Processed {} files.'.format(counter))
        return rval

    @staticmethod
    def rec_void_process(in_dir, ending, process):
        """Apply the given process to all files with the given file ending in the directory and all sub-directories."""
        counter = 0
        for root, dirs, files in os.walk(in_dir):
            for name in files:
                if name.endswith(ending) and not name.startswith('.'):
                    cur = os.path.join(root, name)
                    print('Currently processed file: ' + cur)
                    process(cur)
                    counter += 1
        print('Processed {} files.'.format(counter))

    @staticmethod
    def get_any_file(in_dir, ending):
        """Return the first file found in the given directory that matches the given file ending."""
        for root, dirs, files in os.walk(in_dir):
            for name in files:
                if name.endswith(ending) and not name.startswith('.'):
                    return os.path.join(root, name)

    @staticmethod
    def load_lines_from_file(file):
        """Load the content of the given file to a list of line strings."""
        content = []
        instr = open(file, 'r')
        for line in instr.readlines():
            content.append(line.strip())
        instr.close()
        return content

    @staticmethod
    def write_to_dir(data, out_dir):
        """Write the given data dictionary of file names mapping to file content to a output directory."""

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for file in data.keys():
            f = os.path.join(out_dir, file[file.rfind(os.path.sep)+1:])
            outstr = open(f, 'w')
            for line in data[file]:
                for value in line:
                    outstr.write(value)
            outstr.close()
            print('Written to file ' + f)