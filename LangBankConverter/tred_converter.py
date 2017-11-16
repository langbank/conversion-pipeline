# This script is the entry point for the LangBank conversion pipeline for the use of Tred.
# Copyright (C) 2017 The LangBank Research Group

__author__ = 'zweiss'

import sys
import os
import shutil

import manager.format_manager as fm
import manager.system_manager as sm
import manager.conversion_manager as cm

# TODO
# use send2trash module instead of shutil.rmtree()
# import send2trash
# ...
# send2trash.send2trash(DIR+FILES)

if __name__ == '__main__':

    # Set up
    lib_dir = os.path.sep.join(['..', 'Lib'])
    rsrc_dir = os.path.sep.join([lib_dir, 'rsrc'])
    tmp_dir = os.path.sep.join(['.', 'Tmp'])
    tmp_conll = os.path.sep.join([tmp_dir, 'Conll', ''])
    tmp_ptb = os.path.sep.join([tmp_dir, 'Ptb', ''])
    min_num_args = 3
    exp_num_args = 6
    subdir_demo_to = 'Demos/Data-Conversion/To_PML/'
    subdir_demo_from = 'Demos/Data-Conversion/From_PML/'
    derive_ptb = False
    use_vroot = True
    change_morph = False
    use_stts_lists = True
    help_message = {'0mode': 'either "from" or "to" tred',
                    '1INDIR': 'input directory or "demo"',
                    '2OUTDIR': 'output directory',
                    '3derive_ptb': 'derive PTB files from conll files befor converting to PML',
                    '4use_vroot': 'add a virtual root to each tree to allow more flexible changes in tred',
                    '5\ndemo run': 'run "tred_converter.py to/from demo OUTDIR" to start the demo version. Giving an output directory for the demo is optional. If no output directory is provided, all output is written to the demo folder.'}
    # At least one argument is required. If only one argument is given, it has to be "demo-from" or "demo-to".
    if (len(sys.argv) < min_num_args) or (len(sys.argv) < exp_num_args and not sys.argv[2].lower().startswith('demo')):
        print('Wrong call! Run\n> python3 tred_converter.py mode INDIR OUTDIR derive_ptb use_vroot')
        rval = ''
        for k in sorted(help_message.keys()):
            rval += '\n{} -- {}'.format(k[1:], help_message[k])
        print(rval)
        sys.exit(0)

    # if we are here, we have at least one argument, so it's save to assign the mode
    mode = sys.argv[1].lower()
    convert_to_tred = (mode == 'to')
    in_dir = sys.argv[2]
    print(len(sys.argv))

    # run code on demo data
    if in_dir == 'demo':
        print('Start pipeline demo ...')
        cdir = os.getcwd()[:os.getcwd().rfind('/', 2)+1]
        in_dir = '{}{}in/'.format(cdir, (subdir_demo_to if convert_to_tred else subdir_demo_from))
        out_dir = '{}{}out/'.format(cdir, (subdir_demo_to if convert_to_tred else subdir_demo_from)) if len(sys.argv) < 4 else sys.argv[3]
        # make sure input directory exists
        if not os.path.exists(in_dir):
            print('The demo input is missing. Please make sure to include the folder\n{}\n\nPlease reconstruct the demo'.format(in_dir))
            sys.exit(0)
        # make sure demo output directory is empty (rod = relevant output directory)
        for rod in [out_dir+'const/', out_dir+'deprel/']:
            if os.path.exists(rod) and len(os.listdir(rod)) > 0:
                shutil.rmtree(rod)

    # run code on own data
    else:
        out_dir = sys.argv[3]
        derive_ptb = True if sys.argv[4].lower() == 'true' else False
        use_vroot = True if sys.argv[5].lower() == 'true' else False

    # define output subdirs
    out_dir_const = out_dir+'const/'
    out_dir_deprel = out_dir+'deprel/'
    if not os.path.exists(out_dir_const):
        os.makedirs(out_dir_const)
    if not os.path.exists(out_dir_deprel):
        os.makedirs(out_dir_deprel)

    # make sure tmp is empty
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    if convert_to_tred:
        print('Start converting to Tred\'s PML format.')

        # Derive constituency trees from dependencies if required
        if derive_ptb:
            cm.UniversalTredConverter.convert_conll_to_ptb(in_dir)

        # Load provided constituency and dependency trees for conversion by retrieving all available Conll/PTB data and
        # bringing it to the format that is required by the respective Tred conversion script
        conll_content = sm.FileHandler.rec_rval_process(in_dir, '.conll', lambda x: fm.CONLLFormatter.get_lb_tred_format(x))
        ptb_content = sm.FileHandler.rec_rval_process(in_dir, '.ptb', lambda x: fm.PTBFormatter.get_lb_tred_format(x))

        # Manipulate format to suit requirements of the Tred conversion scripts and save temporary results in tmp dir
        if use_vroot:  # Add virtual roots
            conll_content = fm.CONLLFormatter.add_vroot(conll_content)
            ptb_content = fm.PTBFormatter.add_vroot(ptb_content)

        # Copy schema files to output directory
        shutil.copy(os.path.sep.join([lib_dir, 'pl', 'conll2pml', 'resources', 'partial_droplist_schema.xml']), os.path.sep.join([out_dir_deprel, 'conll_schema.xml']))
        shutil.copy(os.path.sep.join([lib_dir, 'pl', 'ptb2pml', 'resources', 'pennmrg_schema.xml']), os.path.sep.join([out_dir_const, 'ptb_schema.xml']))

        # Save results for interim
        sm.FileHandler.write_to_dir(conll_content, tmp_conll)
        sm.FileHandler.write_to_dir(ptb_content, tmp_ptb)

        # Run tred conversion scripts to convert data to PML format
        cm.UniversalTredConverter.convert_conll_to_pml(out_dir_deprel)
        cm.UniversalTredConverter.convert_ptb_to_pml(out_dir_const)

        # TODO ISSUE in CODE: check on laptop if still there, on mac it is solved!

        # Postprocess tred files in terms of their schema XML files
        # First change schema file given in the pml files and write them to the output directory
        pml_dep = sm.FileHandler.rec_rval_process(tmp_conll, '.pml', lambda x: fm.PMLFormatter.get_lb_tred_format(x, 'conll_schema.xml'))
        sm.FileHandler.write_to_dir(pml_dep, out_dir_deprel)
        pml_const = sm.FileHandler.rec_rval_process(tmp_ptb, '.pml', lambda x: fm.PMLFormatter.get_lb_tred_format(x, 'ptb_schema.xml'))
        sm.FileHandler.write_to_dir(pml_const, out_dir_const)

        # Second, adjust schema files: conll files get drop lists, ptb files are free to write
        fm.PMLFormatter.adjust_schema_to_langbank_dependency_schema_modification(out_dir_deprel, out_dir_deprel, rsrc_dir, use_stts_lists=use_stts_lists, edit_morph_features=change_morph)
        fm.PMLFormatter.adjust_schema_to_langbank_constituency_schema_modification(out_dir_const+'ptb_schema.xml', indent_depth=2)

    else:
        print('Start converting from Tred\'s PML format.')

        # Convert PML to Conll format, only consider files ending in the specified sentence ending
        cm.UniversalTredConverter.convert_pml_to_conll(in_dir, out_dir_deprel, ending='.conll_0000.pml')  # TODO more thorough check, but seems to work, also: currently no reading of conll files possible

        # Convert PML to Conll format, only consider files ending in the specified sentence ending
        #cm.UniversalTredConverter.convert_pml_to_ptb(in_dir, out_dir_const, ending='.ptb.pml')  # TODO

    # Clean up: Remove temporary helper directory
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    print('Done. You may find your results at\n{}'.format(out_dir))