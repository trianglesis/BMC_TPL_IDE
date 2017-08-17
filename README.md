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
    - [ ] check DEV paths; 
    - [ ] pattern uploading;
    - [ ] auto scan start;
- [ ] Start scan
- [ ] Validate results:
    - [ ] si query;  
    - [ ] si models;  
    - [ ] gather record data;  
    - [ ] generate DML data;
    - [ ] generate test data;
      


## Can be added soon:

Now in progress:

- [ ] Pattern upload without checks;
- [ ] root or not-root user;
- [ ] folder autocreation;
- [ ] automatic record and dml data gathering (can be usefull for support);
- [ ] automatic verifying discovered data;
- [ ] better console output;
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
      - Set this to correspond tpl version to upload folder of TPLPreprocessor output result ignoring ADDM tpl version check procedure. Use when you want upload older or newer tpl on ADDMIf file is not a .tplpre - this option will be ignored.
    - *-imp*
      - Set if you want to import patterns only imported in current opened pattern from -full_path. No recursive imports will run. If file is not a .tplpre - this option will be ignored.
    - *-r_imp*
      - Set if you want to import all patterns in recursive mode and upload this package on ADDM.Better use on clear TKN.If file is not a .tplpre - this option will be ignored.
    - *-T* 
      - Run validation process after scan is finished.This will use set of queries to grab everything from scan and build SI models.si_type will be gathered from pattern blocks and used to compose search query.model file will be saved into developers folder: /usr/tideway/TKU/models



### Set your settings or use preconfigured ones.

- How to use Pattern upload:

        This is not recommended now - I working on new 
        logic which should'n use root for any operation.

- How to allow ADDM root so SSH?

Go to vi /etc/ssh/sshd_config and change the options: 

    PermitRootLogin yes
    uncomment port 22
    comment line ‘AllowUsers’
    restart ‘service sshd restart’


## Issues and requests:
Please add issues and requests here: [issues](https://github.com/triaglesis/BMC_TPL_IDE/issues)


# NOTE:
Some features are not working, will update them for public use and add soon!

Last validation: 2017-08-17