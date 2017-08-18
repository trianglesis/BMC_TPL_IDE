"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import os
import zipfile

"""
Here I will compose some settings and paths based on args and settings I can obtain or found.

"""


class LocalLogic:

    def __init__(self, logging):

        self.logging = logging

    def tkn_tree(self, path_parse):
        """
        Compose paths to usual TKN tree dirs

        :return:
        """
        log = self.logging
        print(self.parsable_args_set)
        if self.parsable_args_set['file_ext'] == 'tplpre':
            log.debug("Dev pattern")

        log.debug("Parsing path for options.")

        workspace      = path_parse.group('workspace')
        addm           = path_parse.group('addm')
        tkn_main       = path_parse.group('tkn_main')
        tku_patterns   = path_parse.group('tku_patterns')
        pattern_lib    = path_parse.group('pattern_lib')
        pattern_folder = path_parse.group('pattern_folder')
        file_name      = path_parse.group('file_name')
        file_ext       = path_parse.group('file_ext')

        # Composing some usual places here - to make it easy to manage
        # and not to add this each time further.
        # TODO: Maybe need to check if exist here:
        # TODO: Later move it to local logic from each occurence!
        tkn_main_t = workspace + os.sep + addm + os.sep + tkn_main
        buildscripts_t      = tkn_main_t + os.sep + 'buildscripts'
        tku_patterns_t      = tkn_main_t + os.sep + tku_patterns

        # pep8: disable=
        CORE_t              = tkn_main_t + os.sep + tku_patterns + os.sep + 'CORE'
        MIDDLEWAREDETAILS_t = tkn_main_t + os.sep + tku_patterns + os.sep + 'MIDDLEWAREDETAILS'
        DBDETAILS_t         = tkn_main_t + os.sep + tku_patterns + os.sep + 'DBDETAILS' + \
                                                                   os.sep + 'Database_Structure_Patterns'
        SupportingFiles_t   = tkn_main_t + os.sep + tku_patterns + os.sep + 'CORE' + \
                                                                   os.sep + 'SupportingFiles'
        tkn_sandbox_t       = workspace  + os.sep + addm + os.sep + 'tkn_sandbox'

    def addm_compose_paths(self, dev_vm_path, pattern_folder):
        """
        Local path will be used to compose same path in remote vm if HGFS shares confirmed.
        :return:
        """
        log = self.logging
        # Paths from local to remote:
        # TODO: Maybe need to check if exist here:
        workspace = dev_vm_path

        tkn_main_virt = workspace + "/addm/tkn_main"
        tku_patterns_virt      = tkn_main_virt + "/tku_patterns"
        CORE_virt              = tku_patterns_virt + '/CORE'

        # Not used now, but can be later used:
        # buildscripts_virt      = tkn_main_virt + "/buildscripts"
        # MIDDLEWAREDETAILS_virt = tku_patterns_virt + '/MIDDLEWAREDETAILS'
        # DBDETAILS_virt         = tku_patterns_virt + '/DBDETAILS' + '/Database_Structure_Patterns'
        # SupportingFiles_virt   = tku_patterns_virt + '/CORE'      + '/SupportingFiles'

        # Composing working dir as in def full_path_parse() but now for remote mirror:
        working_dir_virt = CORE_virt+"/"+pattern_folder
        log.debug("ADDM: Virtual working_dir: for addm is: "+str(working_dir_virt))

        return working_dir_virt

    def make_zip(self, path, module_name):
        """
        Zip pattern files in path.
        :param module_name: Name of pattern or its folder to create zip with its name.
        :param path: Path where tpl files are ready to be zipped.
        :return: zip path to ready zip file.
        """
        log = self.logging

        norm_path = os.path.normpath(path+os.sep)
        path = norm_path+os.sep

        log.info("ZIP: Making zip of all .tpl in folder:"  + norm_path)

        zip_filename = module_name + '.zip'

        zip_path = path + zip_filename

        patterns_zip = zipfile.ZipFile(zip_path, 'w')
        log.debug("ZIP: zip_filename:" + zip_filename)

        for foldername, subfolders, filenames in os.walk(norm_path):
            for filename in filenames:
                if filename != zip_filename:
                    patterns_zip.write(os.path.join(norm_path, filename), arcname=filename)
                    log.debug("ZIP: Adding pattern:" + filename)
        patterns_zip.close()

        log.debug("ZIP: zip_path: " + zip_path)

        return zip_path
