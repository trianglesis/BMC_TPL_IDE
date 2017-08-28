# BMC_TPL_IDE

# DEV version currently

    This programm is now in DEV and not working as expected. 
    I plan to release normal working version for Customers and Developers 
    and the end of summer.

This is IDE and automation programm for [BMC Discovery (ADDM)](https://discovery.bmc.com/) language - TPL [tideway pattern language](http://www.bmc.com/it-solutions/discovery-dependency-mapping.html)

##### For tpl syntax highlighting follow:

- Syntax for [Sublime text](https://github.com/triaglesis/bmc_tpl)
- Syntax for [Atom](https://github.com/triaglesis/language-tplpre)


### Designed for Python 3

##### Can run in usual shell or like 'build system'

Just run it from CMD:

    -full_path "d:\ROOT\addm\tkn_main\tku_patterns\CORE\PatternFolderName\PatternName.tplpre" -l "debug" --help


## Current features:
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
- [X] Start scan
- [ ] Validate results:
    - [ ] si query;  
    - [ ] si models;  
    - [ ] gather record data;  
    - [ ] generate DML data;
    - [ ] generate test data;
      


## Can be added soon:

Now in progress:

- [X] Pattern upload without checks;
- [X] root or not-root user;
- [X] folder autocreation;
- [ ] automatic record and dml data gathering (can be usefull for support);
- [ ] automatic verifying discovered data;
- [X] better console output;
- [ ] tests;
- [ ] REST API usage for BMC Discovery;
- [ ] Credentials update;

### Install:

- download project;
- use master/bmc_tplpre;
- copy it wherever you want;
- point your build system to it;
- use arguments;

## Usage:

This is dev example. Args can change soon. Please subscribe for recent changes.

usage: check.py

        [-h] [-tpl VERSION_TPL] [-imp] [-r_imp] [-T] [-full_path FULL_PATH] [-u USER] [-p PASSWORD] [-addm ADDM_HOST] [-host_list SCAN_HOST_LIST] [-disco_mode DISCO_MODE] [-l LOG_LVL] [--version]


- optional arguments:
    - *-h, --help* Show this help message and exit.

- Common options:
    - *-full_path FULL_PATH*
        - Path to current edited or processed file.
    - *-u USER*
        - Your ADDM user - root or tideway
    - *-p PASSWORD*
        - Password for ADDM user
    - *-system_user*
        - Your ADDM system user used to start scan
    - *-system_password*
        - Your ADDM system user password used to start scan
    - *-addm ADDM_HOST*
        - ADDM ip address.
    - *-host_list SCAN_HOST_LIST*
        - Host list to Discovery scan on ADDM sep by comma.
    - *-disco_mode DISCO_MODE*
        - Choose the discovery mode: standard|playback|record
    - *-l LOG_LVL*
        - Please set log level
    - *--version*
        - show program's version number and exit

- Developer options:
    - *-tpl VERSION_TPL*
      - Ignored option. In progress...
    - *-imp*
      - Set if you want to import patterns only imported in current opened pattern from -full_path. No recursive imports will run. If file is not a .tplpre - this option will be ignored.
    - *-recursive_import*
      - Options imports all patterns in recursive mode including each 'imports' from each found pattern.
    - *-usual_import*
      - Option imports patterns which only imported in currently opened pattern
    - *-read_test*
      - Read test.py file and get all patterns which used for test and import in recursive mode.



## Issues and requests:
Please add issues and requests here: [issues](https://github.com/triaglesis/BMC_TPL_IDE/issues)


# NOTE:
Mow working all of usual dev functions.

Last validation: 2017-08-28