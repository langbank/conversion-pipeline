# This script provides simple dependency tree representation to facilitate data format conversions.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

from trees.AbsTree import *


class ConllWord(AbsWord):

    def __init__(self):
        self.idx = ''
        self.form = ''
        self.lemma = ''
        self.postag = ''
        self.features = ''
        self.deprel = ''
        self.phead = ''
        self.pdeprel = ''

    def __len__(self):
        return len(self.form)

    def __str__(self):
        rval = str(self.idx)+'\t'+self.form+'\t'+self.lemma+'\t'+self.postag+'\t'+self.postag+'\t'
        for f in self.features:
            rval += f+'|'
        rval = rval[:-1]+'\t'
        rval += str(self.phead)+'\t'+self.deprel+'\t'+str(self.phead)+'\t'+self.pdeprel+'\n'
        return rval

    def __eq__(self, other):
        return self.form == other.form \
               and self.idx == other.idx \
               and self.lemma == other.lemma \
               and self.postag == other.postag \
               and self.features == other.features \
               and self.deprel == other.deprel \
               and self.phead == other.phead \
               and self.pdeprel == other.pdeprel

    def __ne__(self, other):
        return not self.__eq__(other)


    # setter

    def set_all(self, idx, form, lemma, postag, features, deprel, phead, pdeprel):
        self.set_idx(idx)
        self.set_form(form)
        self.set_lemma(lemma)
        self.set_postag(postag)
        self.set_features(features)
        self.set_deprel(deprel)
        self.set_phead(phead)
        self.set_pdeprel(pdeprel)

    def set_idx(self, idx):
        self.idx = int(idx)

    def set_form(self, form):
        self.form = form

    def set_lemma(self, lemma):
        self.lemma = lemma

    def set_postag(self, postag):
        self.postag = postag

    def set_features(self,features):
        self.features = features

    def set_deprel(self, deprel):
        self.deprel = deprel

    def set_phead(self, phead):
        self.phead = phead

    def set_pdeprel(self, pdeprel):
        self.pdeprel = pdeprel

    # getter

    def get_idx(self):
        return self.idx

    def get_form(self):
        return self.form

    def get_lemma(self):
        return self.lemma

    def get_postag(self):
        return self.postag

    def get_features(self):
        return self.features

    def get_deprel(self):
        return self.deprel

    def get_phead(self):
        return self.phead

    def get_pdeprel(self):
        return self.pdeprel


class ConllSentence(AbsSentence):

    def __init__(self):
        self.words = {}

    def __str__(self):
        rval = ''
        for w in sorted(self.words.keys()):
            rval += str(self.words[w])
        return rval

    def __len__(self):
        return len(self.words.keys())

    # setter

    def set_words(self, words):
        self.words = words

    def set_word(self, word):
        self.words[word.idx] = word

    def set_word_by_idx(self, idx, word):
        self.words[idx] = word

    # getter

    def get_words(self):
        return self.words

    def get_word(self, idx):
        return self.words[idx]

    def add_word(self, word):
        self.words[word.idx] = word

    def add_word_by_idx(self, idx, word):
        self.words[idx] = word

    # static

    @staticmethod
    def read_from_pml_file(file, skip_vroot=True, word_start='<LM order="', sent_start='<LM xml:id="s-', form='<form>', lemma='<lemma>',
                      pos='<postag>', deprel='<deprel>', head='<phead>', pdeprel='<pdeprel>'):
        rval = []
        instr = open(file, 'r')
        is_feature = False
        cur_feats = []
        cur_word = ConllWord()
        cur_sent = ConllSentence()
        lms = 0
        for l in instr.readlines():
            line = l.strip()
            # Ignore empty lines
            if len(line) == 0:
                continue
            # Adjust LM tag count if necessary
            if line.startswith('<LM'):  # open new sub-node
                lms += 1
            if '</LM>' in line:  # close old sub-node
                lms -= 1
            # Build sentence if final sentence sub-node was closed
            if lms == 0:
                if len(cur_sent) > 0:
                    rval.append(cur_sent)
                cur_sent = ConllSentence()
            # Build word if word ends; i.e. either at list of children or single lm closure
            if (line.startswith('<childnodes>') or line.startswith('</LM>')) and not cur_word.idx == '':
                if not (skip_vroot and cur_word.idx == -1):
                    cur_sent.add_word(cur_word)
                cur_word = ConllWord()

            # fill word with information
            elif line.startswith(word_start):
                cur_word.set_idx(line[len(word_start):-2])
            elif line.startswith(form):
                cur_word.set_form(line[len(form):-len(form)-1])
            elif line.startswith(lemma):
                cur_word.set_lemma(line[len(lemma):-len(lemma)-1])
            elif line.startswith(pos):
                cur_word.set_postag(line[len(pos):-len(pos)-1])
            elif line.startswith(deprel):
                cur_word.set_deprel(line[len(deprel):-len(deprel)-1])
            elif line.startswith(head):
                cur_word.set_phead(line[len(head):-len(head)-1])
            elif line.startswith(pdeprel):
                cur_word.set_pdeprel(line[len(pdeprel):-len(pdeprel)-1])
            elif line.startswith('<feats>'):
                cur_feats = []
                is_feature = True
            elif line == '</feats>':
                cur_word.set_features(cur_feats)
                is_feature = False
            elif is_feature and line.startswith('<LM>') and line.endswith('</LM>'):
                cur_feats.append(line[len('<LM>'):-len('</LM>')])

        instr.close()
        return rval

    @staticmethod
    # TODO implement!
    def read_from_file(file): pass

    @staticmethod
    def write_to_file(file, sentences):
        outstr = open(file, 'w')
        for sentence in sentences:
            outstr.write(str(sentence))
            outstr.write('\n')
        outstr.close()
        print('Wrote sentences to ' + file)


if __name__ == '__main__':

    w0 = ConllWord()
    w0.set_all(1, 'I.', 'I.', 'APPR', ['_'], 'ROOT', '-1', 'ROOT')
    w1 = ConllWord()
    w1.set_all(2, 'der', 'der', 'ART', ['gen','sg','fem'], 'NK', '4', 'NK')
    w2 = ConllWord()
    w2.set_all(3, 'weiße', 'weiß', 'ADJA', ['dat','sg','fem','pos'], 'NK', '4', 'NK')
    w3 = ConllWord()
    w3.set_all(4, 'Tannenbaum', 'Tannenbaum', 'NN', ['dat','sg','fem','pos'], 'NK', '1', 'NK')
    w4 = ConllWord()
    w4.set_all(5, '.', '.', '$.', ['_'], 'PUNC', '4', 'PUNC')

    s = ConllSentence()
    s.set_words({1:w0, 2:w1 ,3:w2,4:w3, 5:w4})
    print(s)

    s2 = ConllSentence()
    s2.add_word(w0)
    s2.add_word(w1)
    s2.add_word(w2)
    s2.add_word(w3)
    s2.add_word(w4)
    print(s2)

    text = ConllSentence.read_from_pml_file('/Users/zweiss/Dropbox/current-research/LangBank-Pipeline/AnnotationModule/rsrc/LB_RidgesVersion6.0-Tred_Comp2Korr/tred-dependencies/Wund-Artzney_1652_Greiff.conll_0000.pml')
    len(text)
    for s in text[1:4]:
        print(s)
        print('')