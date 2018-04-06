# This script provides simple dependency tree representation to facilitate data format conversions.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'


from trees.AbsTree import *


class DepWord(AbsWord):

    def __init__(self, form="", order=-1, lemma="", cpostag="", postag="", feats="", head=-1, deprel="", phead=-1, pdeprel=""):
        self.order = order  # The number of the token in the current sentence, starting with 1
        self.form = form  # The form of the token
        self.lemma = lemma  # The lemma of the token
        self.cpostag = cpostag  # Coarse-grained part-of-speech tag
        self.postag = postag  # Fine-grained part-of-speech tag
        self.feats = feats  # Syntactic/morphological/miscellaneous features, separated by the pipe character
        self.head = head  # The ID of this token´s head token (or 0 for none)
        self.deprel = deprel  # Dependency relation to HEAD
        self.phead = phead  # The projective head of the token: an ID or 0 for none
        self.pdeprel = pdeprel  # Dependency relation to PHEAD

    def __len__(self):
        return len(self.form)

    def __str__(self, delim="\t"):
        return "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(self.get_value("order"), delim,
                                                               self.get_value("form"), delim,
                                                               self.get_value("lemma"), delim,
                                                               self.get_value("cpostag"), delim,
                                                               self.get_value("postag"), delim,
                                                               self.get_value("feats"), delim,
                                                               self.get_value("head"), delim,
                                                               self.get_value("deprel"), delim,
                                                               self.get_value("phead"), delim,
                                                               self.get_value("pdeprel"))

    def __eq__(self, other):
        return self.form == other.form \
               and self.order == other.idx \
               and self.lemma == other.lemma \
               and self.postag == other.postag \
               and self.features == other.features \
               and self.deprel == other.deprel \
               and self.phead == other.phead \
               and self.pdeprel == other.pdeprel \
               and self.cpostag == other.cpostag \
               and self.feats == other.feats \
               and self.head== other.head

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return int(self.order) < int(other.order)

    def is_vroot(self, vroot_string='-1\t&lt;vroot>\t&lt;vroot-LEMMA>\t_\tVROOT\t_\t-1\tVROOT\t0\tVROOT\n'):
        return self.order == -1

    # setter

    def set_all(self, order, form, lemma, cpostag, postag, features, deprel, head, phead, pdeprel):
        self.set_order(order)
        self.set_form(form)
        self.set_lemma(lemma)
        self.set_cpostag(cpostag)
        self.set_postag(postag)
        self.set_feats(features)
        self.set_deprel(deprel)
        self.set_head(head)
        self.set_phead(phead)
        self.set_pdeprel(pdeprel)

    def set_order(self, idx):
        self.order = int(idx)

    def set_form(self, form):
        self.form = form

    def set_lemma(self, lemma):
        self.lemma = lemma

    def set_postag(self, postag):
        self.postag = postag

    def set_feats(self, feats):
        self.feats = feats

    def add_feat(self, f, delim='|'):
        self.feats += ('' if len(str(self.feats)) == 0 else delim) + f

    def set_deprel(self, deprel):
        self.deprel = deprel

    def set_phead(self, phead):
        self.phead = phead

    def set_pdeprel(self, pdeprel):
        self.pdeprel = pdeprel

    def set_cpostag(self, cpostag):
        self.cpostag = cpostag

    def set_head(self, head):
        self.head = head

    # getter

    def get_order(self):
        return self.order

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

    def get_value(self, variable, default="_", pEqualsC=False):
        tmp = variable.lower().strip()
        if tmp == 'order' and len(str(self.order)) > 0:
            return self.order
        if tmp == 'form' and len(str(self.form)) > 0:
            return self.form
        if tmp == 'lemma' and len(str(self.lemma)) > 0:
            return self.lemma
        if tmp == 'cpostag':
            if len(str(self.cpostag)) > 0:
                return self.cpostag
            if pEqualsC and len(str(self.postag)) > 0:
                return self.postag
        if tmp == 'postag':
            if len(str(self.postag)) > 0:
                return self.postag
            if pEqualsC and len(str(self.cpostag)) > 0:
                return self.cpostag
        if tmp == 'feats' and len(str(self.feats)) > 0:
            return self.feats
        if tmp == 'head':
            if len(str(self.head)) > 0:
                return self.head
            if pEqualsC and len(str(self.phead)) > 0:
                return self.phead
        if tmp == 'deprel':
            if len(str(self.deprel)) > 0:
                return self.deprel
            if pEqualsC and len(str(self.pdeprel)) > 0:
                return self.pdeprel
        if tmp == 'phead':
            if len(str(self.phead)) > 0:
                return self.phead
            if pEqualsC and len(str(self.head)) > 0:
                return self.head
        if tmp == 'pdeprel':
            if len(str(self.pdeprel)) > 0:
                return self.pdeprel
            if pEqualsC and len(str(self.deprel)) > 0:
                return self.deprel
        return default

    @staticmethod
    def read_conll(string, delim="\t"):
        tmp = string.split(delim)
        if len(tmp) < 10:
            print('Warning: Incorrect input string! '+str(len(tmp)))
            return
        order = tmp[0] if len(tmp) > 0 else 0
        form = tmp[1] if len(tmp) > 1 else "_"
        lemma = tmp[2] if len(tmp) > 2 else "_"
        cpostag = tmp[3] if len(tmp) > 3 else "_"
        postag = tmp[4] if len(tmp) > 4 else "_"
        feats = tmp[5] if len(tmp) > 5 else "_"
        head = tmp[6] if len(tmp) > 6 else "_"
        deprel = tmp[7] if len(tmp) > 7 else "_"
        phead = tmp[8] if len(tmp) > 8 else "_"
        pdeprel = tmp[9] if len(tmp) > 9 else "_"
        return DepWord(form, order, lemma, cpostag, postag, feats, head, deprel, phead, pdeprel)


class DepSentence(AbsSentence):

    def __init__(self):
        self.words = []

    def __str__(self):
        return "\n".join(str(t) for t in self.words)

    def __len__(self):
        return len(self.words)

    # setter

    def set_words(self, words):
        self.words = words

    def set_word(self, word):
        self.words[word.order] = word

    # getter

    def get_words(self):
        return self.words

    def get_word(self, idx, word=''):
        if idx < 0:
            return -1
        if idx >= len(self.words):
            return -1
        return self.words[idx]

    def add_word(self, word):
        self.words.append(word)
        self.words = sorted(self.words)

    def add_conll_string(self, new_string):
        cword = DepWord.read_conll(new_string)
        self.words.append(cword)
        self.words = sorted(self.words)

    # static

    @staticmethod
    def read_from_pml_file(file, skip_vroot=True, tab_length=4):
        skip_vroot = False  # TODO currently lossless vroot removal not possible, ongoing debugging
        rval = []
        with open(file, 'r') as instr:
            s = DepSentence()
            ctok = DepWord()
            mother_node = {}
            has_additional_indent = False
            is_feat = False
            found_body = False
            for line in instr.readlines():
                line = line.replace('\t', ' '*tab_length).replace('&amp;', '&')
                l = line.strip()
                ind = DepSentence.indentation_level(line)
                # ignore everything with less than 2 indentations
                if not found_body:
                    found_body = l == "<body>"
                    continue
                # handle sentence level matters (2 indentations)
                if ind == 2:
                    if l == "</LM>" and len(s) > 0:  # sentence ends
                        has_additional_indent = False
                        if not ctok.is_vroot() or not skip_vroot:  # if it's not a vroot or we don't care if it is
                            s.add_word(ctok)
                        rval.append(s)
                        continue
                    if l.startswith("<LM "):  # new sentence starts
                        s = DepSentence()
                        ctok = DepWord()
                        mother_node = {}
                        has_additional_indent = False  # probably useless
                        is_feat = False
                        continue

                # if here, it is some relevant content on token level
                if "order=" in l:
                    # order here means order WITHIN sentence (due to indentation > 2);
                    # hence: indent level-head idx mapping is encoded here
                    mother_node[ind] = l[l.index("order")+7:-2]
                    # Also, within-sentence order info is always at te beginning of a new token
                    # hence: if the current token is not empty (i.e. was reseted already), save+reset here at the latest
                    if len(ctok) > 0:
                        if not ctok.is_vroot() or not skip_vroot:  # if it's not a vroot or we don't care if it is
                            s.add_word(ctok)
                        else:
                            print('Skip: ' + str(ctok))
                    ctok = DepWord()
                    # And set order (obviously)
                    ctok.set_order(l[l.index("order")+7:-2])
                    # Don't continue here, information whether this element was a childnode or an LM tag is IMPORTANT!
                    if l.startswith("<childnodes"):
                        has_additional_indent = False
                    if l.startswith("<LM ") and not is_feat:
                        # If order attribute is in LM tag, it needs an additional indent, because it is embedded in an
                        # order-less childnodes tag
                        has_additional_indent = True
                    continue

                if l.startswith("<form>"):
                    ctok.set_form(l[len("<form>"):-len("</form>")])
                    continue
                if l.startswith("<lemma>"):
                    ctok.set_lemma(l[len("<lemma>"):-len("</lemma>")])
                    continue
                if l.startswith("<postag>"):
                    ctok.set_postag(l[len("<postag>"):-len("</postag>")])
                    continue
                if l.startswith("<deprel>"):
                    ctok.set_deprel(l[len("<deprel>"):-len("</deprel>")])
                    continue
                if l.startswith("<phead>"):
                    c_head = int(l[len("<phead>"):-len("</phead>")])
                    ctok.set_phead(0 if c_head == -1 and skip_vroot else c_head)
                    # also add the other actual head at this point
                    back = 2 if not has_additional_indent else 3
                    c_head = int(mother_node[ind-back]) if ind-back in mother_node.keys() else -1
                    ctok.set_head((0 if c_head == -1 and skip_vroot else c_head))
                    continue
                if l.startswith("<pdeprel>"):
                    ctok.set_pdeprel(l[len("<pdeprel>"):-len("</pdeprel>")])
                    continue
                if l.startswith("<feats>"):
                    is_feat = True
                    # Careful! Might close immediately, if only one feature is there
                    if l.endswith("</feats>"):
                        is_feat = False
                        ctok.add_feat(l[len("<feats>"):-len("</feats>")])
                    continue
                if l.startswith("</feats>"):
                    is_feat = False
                    continue
                if is_feat and l.startswith('<LM>'):
                    ctok.add_feat(l[len("<LM>"):-len("</LM>")])
                    continue
        return rval

    @staticmethod
    def indentation_level(string, div=2):
        l1 = len(string)
        l2 = len(string.strip()) + (1 if string.endswith('\n') else 0)
        return (l1 - l2) / div

    @staticmethod
    def read_from_file(file, delim="\t"):
        rval = []
        with open(file, 'r') as instr:
            s = DepSentence()
            for line in instr.readlines():
                l = line.strip()
                if len(l) == 0:
                    if len(s) > 0:
                        rval.append(s)
                        s = DepSentence()
                    continue
                s.add_word(DepWord.read_conll(l, delim=delim))
        if len(s) > 0:
            rval.append(s)
        return rval

    @staticmethod
    def write_to_file(file, sentences):
        outstr = open(file, 'w')
        for sentence in sentences:
            outstr.write(str(sentence))
            outstr.write('\n\n')
        outstr.close()
        print('Wrote sentences to ' + file)

