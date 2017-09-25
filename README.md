# BMC_TPL_IDE #

This is IDE and automation program for [BMC Discovery (ADDM)](https://discovery.bmc.com/) language - TPL [tideway pattern language](http://www.bmc.com/it-solutions/discovery-dependency-mapping.html)

##### For tpl syntax highlighting follow: #####

- Syntax for [Sublime text](https://github.com/trianglesis/bmc_tpl)
- Syntax for [Atom](https://github.com/trianglesis/language-tplpre)


### Designed for Python 3 ###

##### Can run in usual shell or like 'build system'

#### Syntax check ####

NOTE: syntax tests (require 3rd party [module tplint](https://communities.bmc.com/docs/DOC-42313) by Ladkau, Matthias)


### Install: ###

- download ZIP;
- use master/bmc_tplpre;
- copy it wherever you want;
- point your build system to it; *see examples below*
- pip install **paramiko**, **progressbar2**
- use arguments;

**Required**:
- To use ADDM over SSH commands: [paramiko](https://github.com/paramiko/paramiko)

Optional:
- To print nice and fancy progress bars for long processes: [progressbar](https://github.com/WoLpH/python-progressbar)

## Usage: ##

Different run mode available:

All available modes described [here in pdf.](https://trianglesis.github.io/BMC_TPL_IDE_auto_pics/Diagrams/TPL%20IDE%20Automation.pdf)

### In editor: ###

- ##### Sublime: use it's build system, [example](https://github.com/trianglesis/bmc_tpl/blob/master/tplpre_various.sublime-build).

![Build](https://trianglesis.github.io/BMC_TPL_IDE_auto_pics/TPL_IDE_Build_Sublime3.png)

You probably should update build file example according to recent arguments.


- ##### Atom: install plugin 'build' and use atom-build.yml [example](https://github.com/trianglesis/language-tplpre/blob/master/.atom-build.yml-EXAMPLE).

![Build](https://trianglesis.github.io/BMC_TPL_IDE_auto_pics/TPL_IDE_Build_Atom.png)


- ### In CMD: ###

Common options:

    D:\>C:\Python34\python.exe D:\BMC_TPL_IDE\bmc_tplpre\check.py -h

    usage: check.py [-h] [-usual_import] [-recursive_import] [-read_test]
                    [-run_test] [-related_tests] [-tpl VERSION_TPL]
                    [-full_path FULL_PATH] [-u USER] [-p PASSWORD]
                    [-system_user SYSTEM_USER] [-system_password SYSTEM_PASSWORD]
                    [-addm ADDM_HOST] [-host_list SCAN_HOST_LIST]
                    [-disco_mode DISCO_MODE] [-l LOG_LVL] [--version]

    optional arguments:
      -h, --help            show this help message and exit


- ### From windows context menu: ###

Run regedit;
Add keys as described:

    Use any usual arguments and add any needed key for all you need.
    Just be sure -full_path '%1' - will call path to active file.

- ![reg_shell](https://trianglesis.github.io/BMC_TPL_IDE_auto_pics/TPL_IDE_Run_shell.png)


## Current features: ##

Some of them is still in progress:

- [X] syntax tests (require 3rd party [module tplint](https://communities.bmc.com/docs/DOC-42313) by Ladkau, Matthias)

- [X] importing linked patterns (working only if dev environment found):
    - [X] from current pattern;
    - [X] from current pattern and each imported;
    - [X] from current pattern and each imported and from test.py;

- [X] Run TPLPreprocessor:
    - [X] on current pattern file;
    - [X] on imported pattern files;

- [X] SSH to ADDM for options:
    - [X] check tpl version;
    - [X] check DEV paths;
    - [X] pattern uploading;
    - [X] auto scan start;

- [X] Start scan;

- [X] Tests
    - [X] Run pattern test;
    - [X] Run pattern related tests;


##### Plan #####
- [ ] Validate results:
    - [ ] si query;
    - [ ] si models;
    - [ ] gather record data;
    - [ ] generate DML data;
    - [ ] generate test data;

## Issues and requests:
Please add issues and requests here: [issues](https://github.com/trianglesis/BMC_TPL_IDE/issues)

## MORE:
Some extra docs and explanations for internal logic you can find here:
[All docs](https://trianglesis.github.io/BMC_TPL_IDE_auto_pics/index.html)