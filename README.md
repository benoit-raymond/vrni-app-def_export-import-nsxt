# vrni-app-def_export-import-nsxt
 
This Python scripts gives you easy tools to:
- Export vRNI Application definition rules to JSON file
- Import vRNI Application definition rules into NSX-T Groups (Groups already created via the following script: [vrni-rule-import-vmc-nsxt](https://github.com/vrealize-network-insight/vrni-rule-import-vmc-nsxt))

This module is not supported by VMware, and comes with no warranties express or implied. Please test and validate its functionality before using in a production environment. If you have any issue please raise a github issue. Tested and compatible with vRNI 6.0, NSX-T 3.1.0,
 

## Requirements
- vRNI Python SDK: [network-insight-sdk-python](https://github.com/vmware/network-insight-sdk-python)
- Python3

## Installation
Before you begin, some prereqs:
- Connectivity to vRNI over HTTPS (443)
- Connectivity to NSX-T Manager or VIP over HTTPS (443)
- vRNI Python SDK: [network-insight-sdk-python](https://github.com/vmware/network-insight-sdk-python)
 - Follow installation procedure
- Python3

## Usage
### Export vRNI application definition to json file
```shell
# python3 export-app-def.py --help
python3 export-app-def.py --helpusage: export-app-def.py [-h] [--deployment_type DEPLOYMENT_TYPE] [--platform_ip PLATFORM_IP] [--username USERNAME] [--password PASSWORD]
                         [--domain_type DOMAIN_TYPE] [--domain_value DOMAIN_VALUE] [--get_vidm_client_id] [--vidm_token VIDM_TOKEN]
                         [--api_token API_TOKEN] [--verbose] [--appname APPNAME] [--jsonfile JSONFILE]

Run Public APIs on vRNI Platform

optional arguments:
  -h, --help            show this help message and exit
  --deployment_type DEPLOYMENT_TYPE
                        Setup deployment type: onprem or vrnic
  --platform_ip PLATFORM_IP
                        IP address of vRNI platform. In case of cluster IP address of Platform-1
  --username USERNAME   user name for authentication
  --password PASSWORD   password for authentication
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
  --jsonfile JSONFILE, -o JSONFILE
                        Exported JSON file location
```
CLI example:
```
python3 export-app-def.py --appname <appname> --jsonfile <filename.json> \
  --platform_ip=<fqdn_vrni> --username <username> --password '<password>' \
  --domain_type LDAP --domain_value=<domain>
```
 
### Import vRNI application definition in NSX-T
