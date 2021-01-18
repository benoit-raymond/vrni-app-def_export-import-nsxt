#################################################################################
#                                                                               #
#  The purpose of this script is to:                                            #
#   1) export one vRNI Application (include all configured Tiers) definition    #
#      in a JSON file.                                                          #
#   2) import into NSX-T vRNI Application Tiers definition in                   #
#      NSX Security Group Expression definition                                 #
#       - Based on previously exported vRNI App-Tier definition (only available #
#          for Tier defined via Security Tag - with a single expression)        #
#       - Based on custom JSON formated files. Following the NSX API            #
#        Groups Expression format                                               #
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
import re

import init_api_client
import swagger_client
#export PYTHONPATH=$PYTHONPÄTH:~/Documents/scripts/network-insight-sdk-python/swagger_client-py2.7.egg                                                

#IgnoreSelfSignedSSLCerts
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Global VARS
logger = logging.getLogger('export-vrni-app-def')
SuffixTier = "-vRNI-Import-Tier"
nsx_domain_id = "default"
suffix_file_export_vrni = "-vrni-app-def.json"

"""Main class for exporting vRNI Application Tier definition"""
def export_to_json(args):
    ### Get App definition and Export to JSON file ###
    logger.info("Getting Applications list")
    if args.verbose:
        print ("Getting Applications list ...")
    application_api = swagger_client.ApplicationsApi()
    params = dict(size=100)
    apps = application_api.list_applications(**params)
    for i in apps.results:
        app = application_api.get_application(i.entity_id)
        if format(app.name) == args.appname:
            logger.info("Extracting Tiers definition for requested application")
            tierList = application_api.list_application_tiers(id=app.entity_id)
            tierList = tierList.to_dict()
            if args.verbose:
                print ("Extracting Tiers definition for requested application " + args.appname + ": ")
                print (format(tierList))
            logger.info("Writing Tiers definition for requested application to output JSON file")
            # Define JSON export file full path
            folder = args.export_folder
            if not args.export_folder.endswith("/"):
                folder = folder + "/"
            json_file_export = folder + args.appname.replace(" ", "-") + suffix_file_export_vrni
            with open(json_file_export, 'w') as json_file:
                if args.verbose:
                    print ("Writing Tiers definition for requested application to output JSON file ...")
                json.dump(tierList, json_file)

def get_NSG_expression(infourl, nsx_auth, headers):
    # Gather current NSX-T Group Definition - Expression value
    response = requests.get(infourl, auth=nsx_auth, verify=False, headers=headers, data={})
    if response.status_code != 200:
        print("Unable to GET Security Group URL : " + infourl + ". Response: ", response.status_code, "\n")
        return None
    else:
        return json.loads(response.text)

def patch_NSG_expression(infourl, nsx_auth, headers, payload):
    return requests.patch(infourl,auth=nsx_auth, verify=False, headers=headers,data=json.dumps(payload))

def import_to_nsx(args):
    ## Get NSX-T user password
    passwd = getpass.getpass('Please enter NSX-T password for username ' + args.nsxtuser + ":  ")
    nsx_auth = (args.nsxtuser, passwd)

    if args.expression_jsonfile :
        # Create NSX-T SG based on JSON Expression file
        with open(args.expression_jsonfile) as json_file:
            data = json.load(json_file)
            if args.verbose:
                print ("Application " + args.appname + " Expression definition: ")
                print (format(data))
            # Parse all Tier of current Application
            for tier in data['results']:
                nsx_group_id = tier['id'] 
                # Get NSG current Expression value
                infourl = 'https://%s/policy/api/v1/infra/domains/%s/groups/%s' % (args.nsxt_fqdn, nsx_domain_id, nsx_group_id)
                headers = {'content-type': 'application/json'}
                data = get_NSG_expression(infourl, nsx_auth, headers)
                # Add to expression imported json file NSX-T group definition
                if len(tier['expression']) > 0 and data is not None:
                    for cur_exp in tier['expression']:
                        data.get("expression").append(cur_exp)
                # Patch Expression for NSG
                infourl = 'https://%s/policy/api/v1/infra/domains/%s/groups/%s' % (args.nsxt_fqdn, nsx_domain_id, nsx_group_id)
                headers = {'content-type': 'application/json'}
                response = patch_NSG_expression(infourl, nsx_auth, headers, data)
                if args.verbose:
                    if response.status_code != 200:
                        print("Unable to update Security Group " + nsx_group_id + ". Response: ", response.status_code, "\n")
                    else:
                        print("Security Group Updated: " + nsx_group_id, "\n")
    else:
        ## Create NSX-T SG based on vRNI App export definition
        folder = args.export_folder
        if not args.export_folder.endswith("/"):
            folder = folder + "/"
        json_file_import = folder + args.appname.replace(" ", "-") + suffix_file_export_vrni
        with open(json_file_import) as json_file:
            data = json.load(json_file)
            if args.verbose:
                print ("Application " + args.appname + " vRNI definition: ")
                print (format(data))
                # Auto-Translate vRNI App Tier definition into NSG
                for tier in data['results']:
                    NSG_id = tier['name'] + SuffixTier
                    expression = {}
                    ## Only support one Condition in Tier definition and only Onbe Security Tag Association
                    if len (tier['group_membership_criteria']) == 1 \
                        and tier['group_membership_criteria'][0]['membership_type'] == "SearchMembershipCriteria" \
                        and re.match(r'SecurityTag\s+=\s+\'([\w-]+)\'', tier['group_membership_criteria'][0]['search_membership_criteria']['filter']):
                        filter = tier['group_membership_criteria'][0]['search_membership_criteria']['filter']
                        m = re.search(r'SecurityTag\s+=\s+\'([\w-]+)\'', filter)
                        expression = {"member_type": "VirtualMachine", "key": "Tag", "operator": "EQUALS", "value": m.group(1), "resource_type": "Condition"}
                    else:
                        # Unsupported automatic translation vRNI into NSX-SG
                        if args.verbose:
                            print("Unsupported automatic translation vRNI into NSX-SG " + NSG_id + ". Tier def must be a single SecurityTag.")
                        continue
                    # Get NSG current Expression value
                    infourl = 'https://%s/policy/api/v1/infra/domains/%s/groups/%s' % (args.nsxt_fqdn, nsx_domain_id, NSG_id)
                    headers = {'content-type': 'application/json'}
                    data = get_NSG_expression(infourl, nsx_auth, headers)
                    # Add to expression imported json file NSX-T group definition
                    if len (tier['group_membership_criteria']) > 0 and data is not None:
                        data.get("expression").append(expression)
                    # Patch Expression for NSG
                    infourl = 'https://%s/policy/api/v1/infra/domains/%s/groups/%s' % (args.nsxt_fqdn, nsx_domain_id, NSG_id)
                    headers = {'content-type': 'application/json'}
                    response = patch_NSG_expression(infourl, nsx_auth, headers, data)
                    if args.verbose:
                        if response.status_code != 200:
                            print("Unable to update Security Group " + NSG_id + ". Response: ", response.status_code, "\n")
                        else:
                            print("Security Group Updated: " + NSG_id, "\n")

def main(args):
    # ONLY Run Export to JSON 
    if args.script_mode == 'EXPORT':
        # Connection to vRNI API (if mode EXPORT + EXPORT_IMPORT)
        logger.info("Connecting to vRNI API")
        if args.verbose:
            print ("Connecting to vRNI API...")
        init_api_client.get_api_client(args)
        # Function to export vRNI App def. to JSON file
        export_to_json(args)
        return
    # ONLY Run Import to NSX-T
    elif args.script_mode == 'IMPORT':
        # Import vRNI App definition to NSG Expression 
        import_to_nsx(args)
        return
    # Export vRNI App Def + Import def in NSG
    elif args.script_mode == 'EXPORT_IMPORT':
        # Connection to vRNI API (if mode EXPORT + EXPORT_IMPORT)
        logger.info("Connecting to vRNI API")
        if args.verbose:
            print ("Connecting to vRNI API...")
        init_api_client.get_api_client(args)
        # Function to export vRNI App def. to JSON file
        export_to_json(args)
        # Import vRNI App definition to NSG Expression 
        import_to_nsx(args)
        return
    else:
        logger.error("script_mode "+ args.script_mode +" Unknown ! ")
        if args.verbose:
            print ("script_mode "+ args.script_mode +" Unknown ! ")
        return
        
def parse_arguments_cli():
    parser = init_api_client.parse_arguments()
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output (print status messages)', default=False)
    parser.add_argument('--appname', '-a', help='Name of application for imported rules without spaces')
    parser.add_argument('--export_folder', help='Folder path for exported files')
    parser.add_argument('--expression_jsonfile', help='NSX-T Security Groups Expression definition JSON file location')
    parser.add_argument('--script_mode', '-i', help='Script Mode: {EXPORT, IMPORT, EXPORT_IMPORT}')
    parser.add_argument('--nsxt_fqdn', help='NSX-T Manager FQDN or VIP')
    parser.add_argument('--nsxtuser', help='NSX-T Username')
    logger.info("Parsing CLI Arguments")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # Parsing CLI Arguments
    logger.info("Starting vRNI Export App Tier Definition script...")
    args = parse_arguments_cli()
    # Starting main actions 
    main(args)
    # ENDING
    if args.verbose:
        print ("Done.")