# vrni-app-def_export-import-nsxt
 
This Python scripts gives you easy tools to:
- Export vRNI Application definition rules to JSON file
- Import vRNI Application definition rules into NSX-T Groups 
  - => (NSX Security Groups **MUST BE** already created *AND EMPTY* via the following script: [vrni-rule-import-vmc-nsxt](https://github.com/vrealize-network-insight/vrni-rule-import-vmc-nsxt))

**Current limitations:**
 - Automatic vRNI App Tier to NSX-T Groups definition only works with vRNI Application Definition using Security Tag. 
 - Only a single member and a single Security Tag must be set in the App. Tier definition
 - vRNI Application Names and Tiers must only contains the following char : \[a-ZA-Z0-9\-\_] *(no spaces or special characters, ...)*
 
This module is not supported by VMware, and comes with no warranties express or implied. Please test and validate its functionality before using in a production environment. If you have any issue please raise a github issue. Tested and compatible with vRNI 6.0, NSX-T 3.1.0,


## Requirements
- vRNI Python SDK: [network-insight-sdk-python](https://github.com/vmware/network-insight-sdk-python)
- Python3

## Installation
Before you begin, some prereqs:
- Connectivity to vRNI over HTTPS (443)
- Connectivity to NSX-T Manager or VIP over HTTPS (443)
- Install vRNI Python SDK: [network-insight-sdk-python](https://github.com/vmware/network-insight-sdk-python)
- Python3

## Usage
```shell
cli % python3 export-import_app-tier-def.py --help
usage: export-import_app-tier-def.py [-h] [--deployment_type DEPLOYMENT_TYPE] [--platform_ip PLATFORM_IP] [--vrniuser VRNIUSER] [--domain_type DOMAIN_TYPE]
                                     [--domain_value DOMAIN_VALUE] [--get_vidm_client_id] [--vidm_token VIDM_TOKEN] [--api_token API_TOKEN] [--verbose] [--appname APPNAME]
                                     [--export_folder EXPORT_FOLDER] [--expression_jsonfile EXPRESSION_JSONFILE] [--script_mode SCRIPT_MODE] [--nsxt_fqdn NSXT_FQDN]
                                     [--nsxtuser NSXTUSER]

Run Public APIs on vRNI Platform

optional arguments:
  -h, --help            show this help message and exit
  --deployment_type DEPLOYMENT_TYPE
                        Setup deployment type: onprem or vrnic
  --platform_ip PLATFORM_IP
                        IP address of vRNI platform. In case of cluster IP address of Platform-1
  --vrniuser VRNIUSER   user name for authentication
  --domain_type DOMAIN_TYPE
                        domain type for authentication: LOCAL or LDAP or VIDM
  --domain_value DOMAIN_VALUE
                        domain value for LDAP user: example.com
  --get_vidm_client_id  Get client-id for making user access-token request to vIDM
  --vidm_token VIDM_TOKEN
                        Provide vidm_token
  --api_token API_TOKEN
                        Provide VRNIC api token
  --verbose, -v         Verbose output (print status messages)
  --appname APPNAME, -a APPNAME
                        Name of application for imported rules without spaces
  --export_folder EXPORT_FOLDER
                        Folder path for exported files
  --expression_jsonfile EXPRESSION_JSONFILE
                        NSX-T Security Groups Expression definition JSON file location
  --script_mode SCRIPT_MODE, -i SCRIPT_MODE
                        Script Mode: {EXPORT, IMPORT, EXPORT_IMPORT}
  --nsxt_fqdn NSXT_FQDN
                        NSX-T Manager FQDN or VIP
  --nsxtuser NSXTUSER   NSX-T Username
```
### HOW TO RUN (CLI examples):
- Pre-requistes:
  - Use the following script to create NSX Groups & FW rules : [vrni-rule-import-vmc-nsxt](https://github.com/vrealize-network-insight/vrni-rule-import-vmc-nsxt)
- Run the script in *Automated mode* (Automatic translation vRNI Application Tier definition into NSX-T Groups):
  ```
  python3 export-import_app-tier-def.py --appname <AppName> --verbose --script_mode EXPORT_IMPORT \
     --nsxt_fqdn <nsx-t-fqdn> --nsxtuser <user> --export_folder /path/to/folder/ \
     --platform_ip=<vrni-fqdn.corp.local> --vrniuser <user@corp.local>  \
     --domain_type LDAP --domain_value=<corp.local>
  ```

- Run the script in *Manual mode* (User must create NSX-T expression syntax based on vrni Tier definition):
  - Step one : Export vRNI Application definitions (with all related tiers)
    ```
    python3 export-import_app-tier-def.py --appname <AppName> --verbose --script_mode EXPORT \
       --export_folder /path/to/folder --platform_ip=<vrni-fqdn.corp.local> --vrniuser <user@corp.local> \
       --domain_type LDAP --domain_value=vmware.com
    ```
  - Step two : Import vRNI Application definitions (with all related tiers) into NSX-T Groups.
    - via JSON NSX-T formarted expression file (see examples for guidance)
      ```
      python3 export-import_app-tier-def.py --appname <AppName> --verbose --script_mode IMPORT \
          --expression_jsonfile </path/to/expression/nsxfile.json> --nsxt_fqdn "nsx-t-fqdn" --nsxtuser admin
      ```
    - via automatic vRNI translation (based on previously exported json file - EXPORT phase)
      ```
      python3 export-import_app-tier-def.py --appname <AppName> --verbose --script_mode IMPORT \
         --nsxt_fqdn <nsx-t-fqdn> --nsxtuser <user> --export_folder /path/to/folder/
      ```

