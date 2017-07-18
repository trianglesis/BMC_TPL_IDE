# BMC_TPL_IDE

Syntax hightlight for BMC Discovery (ADDM) language - TPL (tideway pattern language)

http://www.bmc.com/it-solutions/discovery-dependency-mapping.html And: https://discovery.bmc.com/

Designed for Sublmime text 3


=======
Current features:
- tpl\tplpre syntax highlight
- code autocompletions
- pattern uploading
- auto scan start

Removed from public version:
(but some of them are present in python code)
- engine for local syntax check before upload
- engine for tplpre -> tpl convert

Can be added soon:
- REST API usage for BMC Discovery
- Pattern upload without checks
- root or not-root user
- folder autocreation
- automatic record and dml data gathering (can be usefull for support)
- automatic verifying discovered data
- better console output
- tests


=======
Install:

Copy:
- folder: 'bmc_tplpre' to 'C:\Users\USER\AppData\Roaming\Sublime Text 3\Packages\bmc_tplpre'

- files from: 'User' to 'C:\Users\o.danylchenko\AppData\Roaming\Sublime Text 3\Packages\User'

Set your settings or use preconfigured ones.



=======

How to use Pattern upload:

How to allow ADDM root so SSH?

Go to vi /etc/ssh/sshd_config and change the option to yes PermitRootLogin yes
uncomment port 22
comment line ‘AllowUsers’
restart ‘service sshd restart’

This format with Sublime variables used in build systems
This is common options for build  Collapse source

SYNTAX ONLY:
-wd "$file_path" -l "info"

SYNTAX AND TPLPreproc (folder):
-wd "$file_path" -tpl "11.0" -l "info"

SYNTAX AND TPLPreproc (pattern):
-wd "$file_path" -full_path "$file" -tpl "11.0" -l "info"

SYNTAX AND TPLPreproc AND UPLOAD (folder):
-wd "$file_path" -tpl "11.0" -l "info" -addm "192.168.5.8" -u root -p local_R00T

SYNTAX AND TPLPreproc AND UPLOAD (pattern):
-wd "$file_path" -full_path "$file" -tpl "11.0" -l "info" -addm "192.168.5.8" -u root -p local_R00T

SYNTAX AND TPLPreproc AND UPLOAD AND Scan playback (folder):
-wd "$file_path" -tpl "11.0" -l "info" -addm "192.168.5.8" -u root -p local_R00T -host_list "0.0.0.0" -disco_mode "playback"

SYNTAX AND TPLPreproc AND UPLOAD AND Scan (pattern):
-wd "$file_path" -full_path "$file" -tpl "11.0" -l "info" -addm "192.168.5.8" -u root -p local_R00T -host_list "0.0.0.0" -disco_mode "playback"


Build file format example:
This is a code sections from Sublime build file:
build file format attached in \bmc_tplpre\tplpre_various.sublime-build


=======
Some features are not working, will update them for public use and add soon!