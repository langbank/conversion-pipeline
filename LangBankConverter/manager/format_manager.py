# This script manages formats and conversions for conll, ptb, and pml
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

from abc import abstractmethod, ABCMeta
import manager.system_manager as sm
import os
import sys
import re


class ABSFormatter:

    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_lb_tred_format(in_file): pass


class CONLLFormatter(ABSFormatter):

    @staticmethod
    def get_berkley_gs_format(in_file, add_dummy_sentence=False):
        """Creates 3 column format (id, token, POS) that is required to create Berkeley constituency parse from dependency analysis. Assumes that Berkeley Wrapper is not used.

            Keyword arguments:
            in_file -- input file
            add_dummy_sentence -- add "Das Ende." as dummy tail, which is necessary depending on the version of the Berkeley parser used. (default False)
        """
        rval = []
        instr = open(in_file, 'r')
        for line in instr.readlines():
            split = line.strip().split("\t")
            rval.append(split[1]+'\t'+split[3]+'\n' if len(split) < 2 else '\n')
        instr.close()
        if add_dummy_sentence:
            rval.append('\n')
            rval.append('Das\tART\n')
            rval.append('Ende\tNN\n')
            rval.append('.\t$.\n')
        return rval

    @staticmethod
    def get_lb_tred_format(in_file, adjust_morphology=False):
        """Adjust regular ConLL 2009 Format to format assumed by Tred's conversion script.

            Keyword arguments:
            in_file -- input file
            adjust_morphology -- transforms moprhological information to attribute value format (default False)"""

        rval = []
        instr = open(in_file, 'r')
        for line in instr.readlines():
            split = line.replace('.0', '').strip().split("\t")  # Get rid of irrelevant .0 on numbers

            if len(split) >= 10:
                # duplicate informative head
                #tmp = split[6]
                split[6] = split[8]
                #split[8] = tmp

                # Assign ROOT label instead of -- if head and phead are 0
                if split[6] == '0' and split[8] == '0':
                    split[7] = 'ROOT'
                    split[9] = 'ROOT'

                # Use token as lemma if POS indicates punctuation, also use PUNC label instead of -- everywhere
                # Also correct brackets if they have not been recognized by the parser
                if split[3].startswith('$') or (split[1] == '-LRB-' or split[1] == '-RRB-'):
                    split[2] = split[1]
                    split[7] = 'PUNC'
                    split[9] = 'PUNC'

                # get morphology to attribute value format
                if adjust_morphology:
                    if split[5] != '_':
                        tmp = split[5].split('|')
                        if len(tmp) == 3:
                            split[5] = 'case='+tmp[0]+'|num='+tmp[1]+'|gen='+tmp[2]
                        elif len(tmp) == 4:
                            split[5] = 'case='+tmp[0]+'|num='+tmp[1]+'|gen='+tmp[2]+'|num='+tmp[3]
                        else:
                            split[5] = 'def='+split[5]

            rval.append('\t'.join(split)+'\n')
        instr.close()
        return rval

    @staticmethod
    def add_vroot(data, invasive=True):
        """Adds a virtual root to every sentence.

            Keyword arguments:
            data -- dictionary mapping file names to content
            invasive -- redirects id for deprel of root to vroot (default True)
        """
        vroot_pointer = "0" if invasive else "-1"
        vroot_idx = "-1" if invasive else "0"
        vroot = vroot_idx+"\t<vroot>\t<vroot-LEMMA>\tVROOT\tVROOT\t_\t"+vroot_pointer+"\tVROOT\t"+vroot_pointer+"\tVROOT\n"
        rval = {}
        for file in data.keys():
            tmp = []
            for line in data[file]:
                if line.strip().startswith('1\t'):
                    tmp.append(vroot)
                if invasive and line.strip().endswith('ROOT'):
                    tmp_split = line.strip().split('\t')
                    tmp.append("\t".join(tmp_split[:6]) + '\t-1\tROOT\t-1\tROOT\n')
                else:
                    tmp.append(line)
            rval[file] = tmp
        return rval


class PTBFormatter(ABSFormatter):

    @staticmethod
    def get_lb_tred_format(in_file):
        """Remove redundant outer brackets and replace underscores with hyphens for edge separation.

            Keyword arguments:
            in_file -- input file
        """
        edge_pattern = re.compile('(\([A-Z\*\$\.]+)_([A-Z\*]+)')
        rval = []
        instr = open(in_file, 'r')
        for line in instr.readlines():
            # Remove redundant brackets
            l = line.replace('( (', '(')
            l = l.replace(') )\n', ')\n')
            # Adjust PTB Edges (from underscore to hyphen separation):
            l = re.sub(edge_pattern, r'\1-\2', l)  # l = l.replace('_', '-')
            # Get rid of irrelevant .0 on numbers
            l = l.replace('.0', '')
            rval.append(l)
        instr.close()
        return rval

    @staticmethod
    def add_vroot(data):
        """Adds a virtual root to every sentence.

            Keyword arguments:
            data -- dictionary mapping file names to content
        """
        rval = {}
        for file in data.keys():
            tmp = []
            for tree in data[file]:
                if len(tree.strip()) == 0 or tree.strip() == "(())":
                    continue
                tmp.append('(VROOT '+tree.strip()[:-1]+')\n' if tree.strip().endswith('\n') else '(VROOT '+tree.strip()+')\n')
            rval[file] = tmp
        return rval


class PMLFormatter(ABSFormatter):

    pos_file = 'stts_tiger-postags.txt'
    deprel_file = 'stts_tiger-deprel.txt'

    @staticmethod
    def get_lb_tred_format(in_file, new_schema_file=''):
        """Changes the schema source file in given input PML file to the newly given schema file.

            Keyword arguments:
            in_file -- PML input file that should receive new schema file
            new_schema_file -- name of the new schema file
        """
        instr = open(in_file, 'r')
        new_lines = ""
        for line in instr.readlines():
            if line.strip().startswith('<schema href="'):
                new_lines += '  <schema href="{}" />\n'.format(new_schema_file)
            elif len(line.strip()) == 0:
                continue
            else:
                new_lines += line
        instr.close()

        return new_lines

    @staticmethod
    def adjust_schema_to_langbank_dependency_schema_modification(pml_dir, out_dir, src_dir, use_stts_lists=True, edit_morph_features=False):
        xml_files = sm.FileHandler.list_files_in_dir(pml_dir, ending='.xml')
        pos_set = set([])
        deprel_set = set([])

        # derive POS tags and deprels from separate list unless excplicitly told to derive them from the files
        if use_stts_lists:
            pos_set = set(sm.FileHandler.load_lines_from_file(os.path.sep.join([src_dir, PMLFormatter.pos_file])))
            pos_set.update(['VROOT'])
            pos_set.update(['ROOT'])
            deprel_set = set(sm.FileHandler.load_lines_from_file(os.path.sep.join([src_dir, PMLFormatter.deprel_file])))
            deprel_set.update(['VROOT'])
            deprel_set.update(['ROOT'])
        else:
            conll_files = sm.FileHandler.list_files_in_dir(src_dir, ending='.conll')
            for f in conll_files:
                tmp_pos, tmp_deprel = PMLFormatter.retrieve_lists_pos_deprel_from_file(f)
                pos_set.update(tmp_pos)
                deprel_set.update(tmp_deprel)

        # overwrite old drop lists with new pos and deprel items
        PMLFormatter.adjust_dependency_schema(xml_files, out_dir, sorted(pos_set), sorted(deprel_set))

        # Change representation of morphological features in pml file
        if edit_morph_features:
            pml_files = sm.FileHandler.rec_rval_process(pml_dir, '.pml', lambda x: PMLFormatter.edit_features(x, '|'))
            sm.FileHandler.write_to_dir(pml_files, out_dir)

    @staticmethod
    def edit_features(file, delim=':'):
        instr = open(file, 'r')
        feat_stream = False
        cur_feature = ''
        new_content = ''
        for line in instr.readlines():
            if line.strip().startswith('<feats>'):
                cur_feature = line[:-1]
                feat_stream = True
            elif line.strip().startswith('<LM>') and line.strip().endswith('</LM>') and feat_stream:
                cur_feature += line.strip()
            elif line.strip() == '</feats>':
                cur_feature += line.strip()+'\n'
                new_content += cur_feature.replace('</LM><LM>', delim).replace('</LM>', '').replace('<LM>', '')
                feat_stream = False
                cur_feature = ''
            else:
                new_content += line
        instr.close()
        return new_content

    @staticmethod
    def adjust_dependency_schema(xml_files, out_dir, pos_set, deprel_set):
        first = True
        pos_text = ''
        dep_text = ''
        for f in xml_files:
            if first:
                # create drop down list for pos and dep rel;
                # rewrite content of current schema file to use newly created drop lists
                new_content, pos_text, dep_text = PMLFormatter.make_pml_drop_down_lists(f, pos_set, deprel_set)
                first = False
            else:
                # rewrite content of current schema file to use previously created drop lists
                new_content = PMLFormatter.edit_dependency_schema(f, pos_text, dep_text)
            # save results into new xml file
            out_file = os.path.join(out_dir, f[f.rfind('/')+1:])
            outstr = open(out_file, 'w')
            outstr.write(new_content)
            outstr.close()
            print('Wrote schema to: ' + out_file)

    @staticmethod
    def edit_dependency_schema(file, pos_text, dep_text):
        rval = ''
        instr = open(file, 'r')
        prev_line = ''
        for line in instr.readlines():
            rval += pos_text if prev_line.strip() == '<s:member name="postag">' else dep_text if prev_line.strip() == '<s:member name="deprel">' else line
            prev_line = line
        instr.close()
        return rval

    @staticmethod
    def fill_template_for_pml_drop_down_list(choices, name='', indent=''):
        """Creates a single PML choice template based on a given set of choices"""
        rval = '{}<s:choice name="{}">\n'.format(indent, name)
        for choice in choices:
            rval += '{} <s:value>{}</s:value>\n'.format(indent, choice)
        rval += '{}</s:choice>\n'.format(indent)
        return rval

    @staticmethod
    def fill_template_for_pml_free_choice(name, type, indent=''):
        """Creates a single PML free choice template"""
        return '{}<member name="{}" type="{}.type"><cdata format="any"/></member>\n'.format(indent, name, type)

    @staticmethod
    def make_pml_drop_down_lists(file, pos, deprels):
        """Creates PML drop down list templates for POS choice and deprel choice. Returns the entire file as well as
        the underlying lists for re-use."""
        rval = ''
        pos_text = ''
        dep_text = ''
        instr = open(file, 'r')
        prev_line = ''
        need_pos = True
        for line in instr.readlines():
            # replace current line with set of possible POS tags
            if prev_line.strip() == '<s:member name="postag">':
                if need_pos:
                    need_pos = False
                    pos_text += PMLFormatter.fill_template_for_pml_drop_down_list(pos, name='pos-choice', indent=' ' * (prev_line.index('<') + 1))
                    rval += pos_text
                else:
                    line = prev_line.strip() + line.strip()
            # replace current line with set of possible deprels
            elif prev_line.strip() == '<s:member name="deprel">':
                dep_text += PMLFormatter.fill_template_for_pml_drop_down_list(deprels, name='deprel-choice', indent=' ' * (prev_line.index('<') + 1))
                rval += dep_text
            # add all other lines
            else:
                rval += line if not (line.strip() == '<s:member name="postag">' or prev_line.strip() == '<s:member name="postag"><s:cdata format="any" />') or need_pos else ''
            prev_line = line
        instr.close()
        return rval, pos_text, dep_text

    @staticmethod
    def retrieve_lists_pos_deprel_from_file(in_file):
        pos = []
        deprel = []
        instr = open(in_file, 'r')
        for line in instr.readlines():
            cols = line.split('\t')
            # ignore files with too few splits to be a conll format content file
            if len(cols) < 9:
                continue
            # get pos tags and dependency relations
            pos.append(cols[3])
            pos.append(cols[4])
            deprel.append(cols[7])
            deprel.append(cols[9][:-1])
        instr.close()
        return pos, deprel

    @staticmethod
    def adjust_schema_to_langbank_constituency_schema_modification(schema_file, indent_depth=2):
        """Removes droplist for POS, category and function in favor of free entry."""
        rval = ''
        instr = open(schema_file, 'r')
        in_droplist = False
        for line in instr.readlines():
            l = line.strip()

            # ignore content while reading drop list
            if in_droplist:
                if line.strip() == '</type>':  # droplist ends
                    in_droplist = False
                continue

            # ignore postag droplist altogether; any content information was added in initial type set up, cf. next if
            if l == '<type name="postag.type">':
                in_droplist = True
                continue
            # adjust content type for pos when it's defined as member
            if l.startswith('<member name="pos" type="postag.type"/>'):
                cur_name = l[l.find('name="')+6:l.find('" ')]  # i.e. pos, cat, or function
                cur_type = l[l.rfind('type="')+6:l.find('.type')]  # i.e. postag, cat, or function
                rval += PMLFormatter.fill_template_for_pml_free_choice(cur_name, cur_type, ' '*round((len(line)-len(l))/indent_depth))
                continue
            # for cat and function droplist, replace it with an any content statement
            if l == '<type name="function.type">' or l == '<type name="cat.type">':
                in_droplist = True
                ind = round((len(line)-len(l))/indent_depth)
                rval += '{}{}<cdata format="any"/>\n{}</type>\n'.format(line, ' '*(ind+1), ' '*ind)
                continue

            rval += line
        instr.close()
        outstr = open(schema_file, 'w')
        outstr.write(rval)
        outstr.close()
