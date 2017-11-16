# This script provides simple tree representation to facilitate data format conversions.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'


class Terminal():

    def __init__(self, pos, tok):
        self.tok = tok
        self.pos = pos

    def get_pos(self):
        return self.pos

    def get_token(self):
        return self.tok

    def set_pos(self, pos):
        self.pos = pos

    def set_token(self, token):
        self.tok = token

    def __str__(self):
        return '('+self.pos+' '+self.tok+')'


class NonTerminal():

    def __init__(self, pos):
        self.pos = pos
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def insert_child(self, child, idx):
        self.children.insert(idx, child)

    def get_children(self):
        return self.children

    def get_pos(self):
        return self.pos

    def set_children(self, children):
        self.children = children

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        rval = '('+self.pos+' '
        for child in self.children:
            rval += str(child) + ' '
        return rval.strip()+')'

    @staticmethod
    def read_from_pml_file(file):
        rval = []
        instr = open(file)
        type = 0  # -1: non-terminal; 1: terminal
        started_trees = False
        for l in instr.readlines():
            line = l.strip()
            if len(line) == 0:
                continue
            if line == '</trees>':
                break
            if line == '<trees>':
                started_trees = True
            while not started_trees:
                continue
            if line.startswith('<LM '):
                cur_cat = ''
                cur_children = []
                for l in instr.readlines():
                    line2 = l.strip()
                    if line2 == '</LM>':
                        break
                    if line2.startswith('<cat>'):
                        cat = line2[line2.index('>')+1:line2.rfind('<')]
                    # TODO

                cur_tree = NonTerminal(cur_cat)
                cur_tree.set_children(cur_children)
                rval.append(cur_tree)
        instr.close()
        return rval

    @staticmethod
    def write_to_file(file, sentences):
        outstr = open(file, 'w')
        for sentence in sentences:
            outstr.write(str(sentence))
            outstr.write('\n')
        outstr.close()
        print('Wrote sentences to ' + file)


if __name__ == '__main__':

    t0 = Terminal('ART', 'Die')
    t1 = Terminal('NN', 'Löwen')
    t2 = Terminal('VVFIN', 'fressen')
    print(t2)

    nt0 = NonTerminal('NP')
    nt0.add_child(t0)
    nt0.add_child(t1)
    print(nt0)

    nt1 = NonTerminal('VP')
    nt1.add_child(t2)
    print(nt1)

    sent = NonTerminal('S')
    sent.set_children([nt0, nt1])
    print(sent)
