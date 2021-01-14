#################################################################################
#                                                                               #
#  The purpose of this script is to export one vRNI Application Tier            #
#  definition in an exported JSON file                                          #
#                                                                               #
#################################################################################


### Package Imports ####
import requests
import sys
import os
import argparse
import getpass
import json
import logging

import init_api_client
import swagger_client


#IgnoreSelfSignedSSLCerts
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger('export-vrni-app-def')

"""Main class for exporting vRNI Application Tier definition"""
def main(args):
    ### Get App definition ###
    logger.info("Getting Applications list")
    application_api = swagger_client.ApplicationsApi()
    params = dict(size=100)
    apps = application_api.list_applications(**params)
    for i in apps.results:
        app = application_api.get_application(i.entity_id)
        if format(app.name) == args.appname:
            logger.info("Extracting Tiers definition for requested application")
            tiers = application_api.list_application_tiers(id=app.entity_id)
            tiers = tiers.to_dict()
            tiers_to_json = json.dumps(tiers)
            logger.info("Writing Tiers definition for requested application to output JSON file")
            with open(args.jsonfile, 'w') as json_file:
                json.dump(tiers_to_json, json_file)

def parse_arguments_cli():
    parser = init_api_client.parse_arguments()
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output (print status messages)')
    parser.add_argument('--appname', '-a', help='Name of application for imported rules without spaces')
    parser.add_argument('--jsonfile', '-o', help='Exported JSON file location')
    logger.info("Parsing CLI Arguments")
    args = parser.parse_args()
    return args

### Example of CLI usage : 
# python3 export-app-def.py --appname <appname> --jsonfile <filename.json> \
#  --platform_ip=<fqdn_vrni> --username <username> --password '<password>' \
#  --domain_type LDAP --domain_value=<domain>
#
if __name__ == "__main__":
    logger.info("Starting vRNI Export App Tier Definition script...")
    args = parse_arguments_cli()
    logger.info("Connecting to vRNI API")
    api_client = init_api_client.get_api_client(args)
    logger.info("Starting vRNI extract")
    main(args)