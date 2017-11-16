# This script facilitates conversions from and to various data formats.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

import os
from trees import DepTree, Tree
import subprocess
import manager.system_manager as sm


class UniversalTredConverter:
    # TODO finish implementations

    lib_dir = os.path.sep.join(['..', 'Lib'])
    lib_java = os.path.sep.join([lib_dir, 'java'])
    lib_perl = os.path.sep.join([lib_dir, 'pl'])

    @staticmethod
    def convert_conll_to_pml(out_dir):
        """Convert from LangBank Conll format to Tred PML format.

            Keyword arguments:
            out_dir -- output directory
        """
        conll_path = os.getcwd()+'/Tmp/Conll'
        p_command = 'for i in '+conll_path+'/*.conll; do perl "conll2pml" --out-prefix "$i" --technical-root --max-sentences 500 --columns "ID,FORM,LEMMA,POSTAG,POSTAG,FEATS,HEAD,DEPREL,PHEAD,PDEPREL" "$i"; done'
        with(sm.TempChwd(os.path.sep.join([UniversalTredConverter.lib_perl, 'conll2pml']))):
            subprocess.call(p_command, stdout=subprocess.PIPE, shell=True)
            #os.popen('for i in '+conll_path+'/*.conll; do perl "conll2pml" '+params+' "$i"; done')
            #schema_file = sm.FileHandler.get_any_file(conll_path, '.xml')
            #shutil.copy(schema_file, os.path.join(out_dir, 'conll_schema.xml'))
            #shutil.copy(os.path.sep.join(['resources', 'partial_droplist_schema.xml']), os.path.sep.join([out_dir, 'conll_schema.xml']))

    @staticmethod
    def convert_ptb_to_pml(out_dir):
        """Convert from Berkeley PTB format to Tred PML format.

            Keyword arguments:
            out_dir -- output directory
        """
        ptb_path = os.getcwd()+'/Tmp/Ptb'
        p_command = 'for i in '+ptb_path+'/*.ptb; do perl "penn2pml.pl" --output-dir "'+ptb_path+'" --bracketed-terminals "$i"; done'
        with(sm.TempChwd(os.path.sep.join([UniversalTredConverter.lib_perl, 'ptb2pml', 'bin']))):
            subprocess.call(p_command, stdout=subprocess.PIPE, shell=True)
            #os.popen('for i in '+ptb_path+'/*.ptb; do perl "penn2pml.pl" --output-dir "'+ptb_path+'" --bracketed-terminals "$i"; done')
            #shutil.copy(os.path.sep.join(['..', 'resources', 'pennmrg_schema.xml']), os.path.sep.join([out_dir, 'ptb_schema.xml']))

    @staticmethod
    def convert_conll_to_ptb(in_dir, verbose=True):
        """Convert from LangBank Conll format to Berkeley PTB format.

            Keyword arguments:
            in_dir -- input directory
            verbose -- true if user should be warned for long runtime (default True)
        """
        if verbose:
            print('Warning: This process may take a considerable amount of time.')

        with(sm.TempChwd(UniversalTredConverter.lib_java)):
            #subprocess.run(['java', '-cp', '../lib/*:', 'BerkeleyConnl2Ptb', in_dir])
            subprocess.run(['java', '-jar', 'Conll2PtbWrapper_fat.jar', in_dir, os.path.sep.join(['.', 'conll2ptb-wrapper', 'rsrc', 'ger_sm5_gf.gr'])])

    @staticmethod
    def convert_pml_to_conll(in_dir, out_dir, ending='.conll_0000.pml'):
        """Convert from Tred PML format to Conll format.

            Keyword arguments:
            in_dir -- input directory
            out_dir -- output directory
        """

        # read all pml dependencies as conll format texts
        dependency_data = sm.FileHandler.rec_rval_process(in_dir, ending, lambda x: DepTree.ConllSentence.read_from_pml_file(x))

        # write all texts to conll format files
        for file in dependency_data.keys():
            cur = os.path.join(out_dir, file[file.rfind('/')+1:-len(ending)]+'.conll')
            DepTree.ConllSentence.write_to_file(cur, dependency_data[file])

    @staticmethod
    def convert_pml_to_ptb(in_dir, out_dir, ending='.ptb.pml'):
        """Convert from Tred PML format to PTB format.

            Keyword arguments:
            in_dir -- input directory
            out_dir -- output directory
        """

        # dummy until not implemented
        not_implemented = True
        if not_implemented:
            print('Conversion from PML to PTB has not yet been implemented.')
            pass

        # read all pml constituencies as conll format texts
        constituency_data = sm.FileHandler.rec_rval_process(in_dir, ending, lambda x: Tree.NonTerminal.read_from_pml_file(x))

        # write all texts to conll format files
        for file in constituency_data.keys():
            cur = os.path.join(out_dir, file[file.rfind('/')+1:-len(ending)]+'.ptb')
            Tree.NonTerminal.write_to_file(cur, constituency_data[file])


