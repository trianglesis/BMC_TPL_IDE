# BMC_TPL_IDE

# DEV version currently

    This programm is now in DEV and not working as expected.
    I plan to release normal working version for Customers and Developers
    and the end of summer.

This is IDE and automation program for [BMC Discovery (ADDM)](https://discovery.bmc.com/) language - TPL [tideway pattern language](http://www.bmc.com/it-solutions/discovery-dependency-mapping.html)

##### For tpl syntax highlighting follow:

- Syntax for [Sublime text](https://github.com/trianglesis/bmc_tpl)
- Syntax for [Atom](https://github.com/trianglesis/language-tplpre)


### Designed for Python 3

##### Can run in usual shell or like 'build system'

Just run it from CMD:
#### Usage ####

    -full_path "d:\addm\tkn_main\tku_patterns\CORE\PatternFolder\Pattern.tplpre" --help

#### Syntax check ####
NOTE: syntax tests (require 3rd party [module tplint](https://communities.bmc.com/docs/DOC-42313) by Ladkau, Matthias)


### Install: ###

- download ZIP;
- use master/bmc_tplpre;
- copy it wherever you want;
- point your build system to it;
- use arguments;


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
- [X] Start scan;
- [X] Run pattern test;
- [X] Run pattern related tests;


##### Plan #####
- [ ] Validate results:
    - [ ] si query;
    - [ ] si models;
    - [ ] gather record data;
    - [ ] generate DML data;
    - [ ] generate test data;


## Usage: ##

Different run mode available:

### In editor: ###

Sublime: use it's build system, [example](https://github.com/trianglesis/bmc_tpl/blob/master/tplpre_various.sublime-build).

Atom: install plugin 'build' and use atom-build.yml [example](https://github.com/trianglesis/language-tplpre/blob/master/.atom-build.yml-EXAMPLE).

### In CMD: ###


### From windows context menu: ###



## Issues and requests:
Please add issues and requests here: [issues](https://github.com/trianglesis/BMC_TPL_IDE/issues)


# NOTE:
Mow working all of usual dev functions.

Last validation: 2017-08-28