# BMC_TPL_IDE

This is not a Syntax hightlight.
Syntax for [Sublime text](https://github.com/triaglesis/bmc_tpl)
Syntax for [Atom](https://github.com/triaglesis/language-tplpre)

This is IDE and automation programm for BMC Discovery (ADDM) language - TPL (tideway pattern language) http://www.bmc.com/it-solutions/discovery-dependency-mapping.html And: https://discovery.bmc.com/

### Designed for Python 3

##### Can run in usual shell or like build system

## Current features:
- syntax tests (require 3rd party [module tplint](https://communities.bmc.com/docs/DOC-42313) by Ladkau, Matthias)
- automation
- pattern uploading
- auto scan start


## Can be added soon:
- REST API usage for BMC Discovery
- Pattern upload without checks
- root or not-root user
- folder autocreation
- automatic record and dml data gathering (can be usefull for support)
- automatic verifying discovered data
- better console output
- tests

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

This is not recommended now - I working on new logic which should'n use root for any operation.

- How to allow ADDM root so SSH?

Go to vi /etc/ssh/sshd_config and change the option to yes PermitRootLogin yes
uncomment port 22
comment line ‘AllowUsers’
restart ‘service sshd restart’


# NOTE:
Some features are not working, will update them for public use and add soon!

Last validation: 2017-08-17