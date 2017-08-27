"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import os
import zipfile


class LocalLogic:

    def __init__(self, logging):
        """
        Gathering local options based on filesystem arguments and cmd results got on working machine.

        :param logging: func
        """

        self.logging = logging

    def addm_compose_paths(self, dev_vm_path, pattern_folder):
        """
        Local path will be used to compose same path in remote vm if HGFS shares confirmed.
        :return:
        """
        log = self.logging
        # Paths from local to remote:
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
        log.debug("Mirrored working dir for ADDM VM is: "+str(working_dir_virt))

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

        try:
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

        except FileNotFoundError as e:
            log.error("Patterns cannot be zipped because file path does not exist: "+str(e))
            return False
