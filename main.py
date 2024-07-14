#!/usr/bin/python3

import os
import sys
import getopt
import time
from helpers import load_conf
from core import subdomain_scan,web_discovery
import nv


config_file_path = "./etc/config.yaml"
config = {}

nightvision_token = None


nightvision_project_id = None
nightvision_project_name = None

# the list of targets to perform recon against.
targets = []
# the list of excluded subdomains.
ex_subdomains = []
# the path of output dir.
out_dir = ""

create_nightvision_targets = False

# verbose option.
verbose = False

# file path for list of additional subdomains to be included in the recon process.
extra_subs_path = ""

# file path for list of additional subdomains to be included in the recon process (will not be excluded).

included_subs_path = ""

cli_args = sys.argv[1:]



logo = r"""
 _   _ _       _     _ __     ___     _             
| \ | (_) __ _| |__ | |\ \   / (_)___(_) ___  _ __  
|  \| | |/ _` | '_ \| __\ \ / /| / __| |/ _ \| '_ \ 
| |\  | | (_| | | | | |_ \ V / | \__ \ | (_) | | | |
|_| \_|_|\__, |_| |_|\__| \_/  |_|___/_|\___/|_| |_|
         |___/                                      

"""


def showHelpMenu():

    usage = """
    Usage: python3 main.py [Flags]

    Flags:

        -t aka --target (required)                            a single target to perform reconnaissance on it.

        -l aka --list (required)                              a list of the of one or more targets.

        -o aka --output (required)                            output folder path.

        -e aka --excluded (optional)                          the list of the excluded subdomains.

        -h aka --help (optional)                              to show the help menu.

        --conf (optional)                                     path of the custom configuration file (yaml or json).

        -i, --include-subs (optional)                         a list of additional subdomains to be included in the recon process (eg. to not be excluded).

        --ct, --create-nightvision-targets (optional)         create nightvision targets from the collected live http/https subdomains.
        
        --token (optional)                                    nightvision api token, when the option --ct is used.

        --project-id (optional)                               nightvision project id.

        --project-name (optional)                             nightvision project name.


    Examples: 
        
        1- python3 main.py -t example.com -o /home/example -e ex1.example.com,ex2-*.example.com

        2- python3 main.py -t oppo.com -e *.community.oppo.com,bbs.oppo.com --ct --project-name oppo_3 --token (your_token)
            
    """  

    print(usage)



# loading the command line options.
opts = []
args = []

try:
    opts,args = getopt.getopt(cli_args,"t:l:o:e:i:vh",["target=","list=","include-subs=","outdir=","excluded=","conf=","extra-subs=","verbose","help","ct","create-nightvision-targets","token=","project-id=","project-name="])

except Exception as ex:
    showHelpMenu()
    sys.exit(1)

for opt,arg in opts:

    if "-t" == opt or "--target" == opt:

        targets.append(str(arg))

    elif "-l" == opt or "--list" == opt:

        if ".txt" in str(arg):

            if os.path.isfile(str(arg)):
                with open(str(arg),"r") as f:

                    line = str(f.readline()).replace("\n","")

                    while len(line) > 0:
                        targets.append(line)
                        line = str(f.readline()).replace("\n","")
            
            else:
                pass
        else:
            targets = str(arg).split(",")

    elif "-o" == opt or "--outdir" == opt:
        out_dir = str(arg)

        if out_dir == "":
            showHelpMenu()
            exit(1)


    elif "-e" == opt or "--excluded" == opt:

        ex = str(arg)
        ex_lst = []

        if ".txt" in arg:
            if os.path.isfile(arg):

                with open(str(arg),"r") as f:

                    e_sub = str(f.readline()).replace("\n","")

                    while len(e_sub) > 0:

                        ex_lst.append(e_sub)
                        e_sub = str(f.readline()).replace("\n","")
                    
            else:
                pass
        else:
            ex_lst = str(arg).split(",")
        
        for ex_sub in ex_lst:

            ex_subdomains.append(ex_sub)

    elif "--conf" == opt:
        config_file_path = str(arg)
    
    elif "-v" == opt or "--verbose" == opt:
        verbose = True
    elif "-h" == opt or "--help" == opt:
        showHelpMenu()
        sys.exit(0)
    
    elif "--include-subs" == opt or "-i" == opt:
        included_subs_path = str(arg)

    elif "--ct" == opt or "--create-nightvision-targets" == opt:

        create_nightvision_targets = True
    
    elif "--token" == opt:
        
        nightvision_token = str(arg)

    elif "--project-id" == opt:
        nightvision_project_id = str(arg)
    
    elif "--project-name" == opt:
        nightvision_project_name = str(arg)

    else:
        pass



# checking if some options are stored in env and loading them.

for key,val in os.environ.items():

    if key == "NV_TOKEN":
        nightvision_token = str(val)
    
    elif key == "NV_TARGET":
        targets.append(str(val))

    elif key == "NV_PROJECT_NAME":
        nightvision_project_name = str(val)

    elif key == "NV_PROJECT_ID":
        nightvision_project_id = str(val)
    
    elif key == "CREATE_TARGETS":
        create_nightvision_targets = bool(val)

    elif key == "NV_CONFIG":
        config_file_path = str(val)

# printing the logo.
print(logo)

# check if at least there is one target specfed by the user.
if len(targets) == 0:
    showHelpMenu()
    sys.exit(1)

# checking if the config file is exist.
if os.path.isfile(config_file_path) == False:
    print(f"Config file {config_file_path} not found!\n")
    sys.exit(1)

if len(out_dir) == 0:

    out_dir = "./out"



def recon(domain,conf,excluded_subdomains=None,included_subdomains=None):

    
    # creating a list of wildcard excluded subdomains each element in the list
    # is a regex that repersent or match a wildcard excluded subdomain.
    ex_wildcard_subdomains = []
    ex_normal_subdomains = []
    

    
    # checking if the list of excluded subdomains is specified
    if excluded_subdomains is not None:

        for ex_sub in excluded_subdomains:

            # checking the subdomain is wildcard subdomain
            if "*" in ex_sub:
                
                # creating a regext that matches the wildcard subdomain and adding it to `ex_wildcard_subdomains` list.
                regex_str = ex_sub.replace(r".",r"\.").replace(r"*",r".*")
                ex_wildcard_subdomains.append(regex_str)

            else:
                # adding the normal subdomain to `ex_normal_subdomains` list.
                ex_normal_subdomains.append(ex_sub)
            


    target_out_dir = f"{out_dir}/{domain}"
    if os.path.isdir(target_out_dir) == False:
        os.makedirs(target_out_dir)  

    target_temp_dir = target_out_dir+"/temp"
    if os.path.isdir(target_temp_dir) == False:
        os.makedirs(target_temp_dir)  

    try:
        subdomain_scan(domain,conf,target_out_dir,ex_normal_subdomains,ex_wildcard_subdomains,[],included_subdomains)
        live_target_urls = web_discovery(target_out_dir,conf,f"{target_out_dir}/subdomains.txt")

        if create_nightvision_targets:
            
            if nightvision_token is not None:
                
                if nightvision_project_id is not None:
                    
                    nv.create_targets(targets_lst=live_target_urls,nightvision_token=nightvision_token,project_id=nightvision_project_id)

                elif nightvision_project_name is not None:

                    nv.create_targets(targets_lst=live_target_urls,nightvision_token=nightvision_token,project_name=nightvision_project_name)
                
                else:

                    nv.create_targets(targets_lst=live_target_urls,nightvision_token=nightvision_token)
                
                print(f"{len(live_target_urls)} live targets collected for {domain}\n")


            else:
                print("Please specify your NightVision token using '--token' option!\n")


    except Exception as ex:
        print(ex)


def main():


    if os.path.isdir(out_dir) == False:
        os.makedirs(out_dir)
    
    # loading the configuration file and saving its content in the conf dictionary.
    
    config = load_conf(config_file_path)

    # looping through the targets list.
    for target in targets:

        recon(target,config,excluded_subdomains=ex_subdomains,included_subdomains=included_subs_path)
        time.sleep(3)
    
    

    print("\n\nReconnaissance Done.\n")



if __name__ == "__main__":
    main()

        