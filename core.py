import subprocess
import os
import json
import requests
import re
from helpers import is_wildcard_exculded,filter_live_urls
from settings import GITHUB_TOOLS_PATH,WORDLISTS_PATH


def subdomain_scan(domain,scan_config,parent_outdir,ex_subdomains,ex_wildcard_subdomains,extra_subdomains,included_subdomains):


    config = scan_config["subdomain_discovery"]

    tools = config["tools"]

    temp_subdomain_files = tools
    
    # checking if there is additional subdomains specified using the --include-subs option and if yes
    # then storing them in sub-included temp file.
    if (included_subdomains is not None) and (len(included_subdomains) > 0):
        
        with open(f"{parent_outdir}/temp/sub-included.txt","w") as f:

            pattern = re.compile(r".+\."+str(domain))

            for sub in included_subdomains:
                matches = pattern.findall(sub)

                try:
                    included_subdomain = str(matches[0])
                    f.write(f"{included_subdomain}\n")
                except Exception as ex:
                    pass
        

    # checking if there is additional subdomains specified using the --extra-subs option and if yes
    # then storing them in sub-extra.txt temp file.
    if (extra_subdomains is not None) and (len(extra_subdomains) > 0):

        temp_subdomain_files.append("extra")
    
        with open(f"{parent_outdir}/temp/sub-extra.txt","w") as f:

            pattern = re.compile(r".+\."+str(domain))
            
            for sub in extra_subdomains:
                matches = pattern.findall(sub)

                try:
                    extra_subdomain = str(matches[0])
                    f.write(f"{extra_subdomain}\n")
                except Exception as ex:
                    pass

    # fetching subdomains using subfinder.

    if "subfinder" in tools:
        proc = subprocess.Popen(f"subfinder -d {domain} -o {parent_outdir}/temp/sub-subfinder.txt -silent",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()


    if "sublist3r" in tools:

        # fetching subdomains using sublist3r.
        sublist3r_max_ret = 2
        proc = subprocess.Popen(f"python3 {GITHUB_TOOLS_PATH}/Sublist3r/sublist3r.py -d {domain} -e baidu,yahoo,google,bing,ask,netcraft,threatcrowd,ssl,passivedns -o {parent_outdir}/temp/sub-sublist3r-1.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()

        i_max = 0
        while os.path.isfile("{}/temp/sub-sublist3r-1.txt".format(parent_outdir)) == False and i_max < sublist3r_max_ret:
            

            proc = subprocess.Popen(f"python3 {GITHUB_TOOLS_PATH}/Sublist3r/sublist3r.py -d {domain} -e baidu,yahoo,google,bing,ask,netcraft,threatcrowd,ssl,passivedns -o {parent_outdir}/temp/sub-sublist3r-1.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            
            i_max+=1

        sublist3r_temp1_subs = []
        
        # removing the <BR> bad character from sublist3r output.

        if os.path.isfile("{}/temp/sub-sublist3r-1.txt".format(parent_outdir)):
            with open("{}/temp/sub-sublist3r-1.txt".format(parent_outdir),"r") as fr:

                line = str(fr.readline())

                while len(line) > 0:
                    sublist3r_temp1_subs.append(line.replace("<BR>","\n"))
                    line = str(fr.readline())
            
                with open("{}/temp/sub-sublist3r-2.txt".format(parent_outdir),"w") as fw:

                    for subd in sublist3r_temp1_subs:
                        fw.write(subd)
            

            proc = subprocess.Popen(f"rm {parent_outdir}/temp/sub-sublist3r-1.txt && mv {parent_outdir}/temp/sub-sublist3r-2.txt {parent_outdir}/temp/sub-sublist3r.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()

        else:

            temp_subdomain_files.remove("sublist3r")


    

    if "virustotal" in tools:

        # fetching subdomains using virustotal API.

        with open(f"{parent_outdir}/temp/sub-virustotal.txt","w") as f:

            api_key = str(config["api_keys"]["virustotal"])
            subs = []

            try:
                resp = requests.get(f"https://www.virustotal.com/vtapi/v2/domain/report?apikey={api_key}&domain={domain}")
                json_resp = json.loads(resp.text)

                subs = json_resp["subdomains"]

            except Exception as ex:
                pass

            
            if len(subs) > 0:

                for sub in subs:
                    f.write(sub+"\n")

        
    


    if "amass-passive" in tools:
        # fetching subdomains using amass.

        proc = subprocess.Popen(f"amass enum -passive -d {domain} -o {parent_outdir}/temp/sub-amass-passive.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()


    if "amass-active" in tools:
        # fetching subdomains using amass.

        proc = subprocess.Popen(f"amass enum -active -d {domain} -o {parent_outdir}/temp/sub-amass-active.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()

    if "gobuster" in tools:
        # fetching subdomains via subdomain brutefroce using gobuster.

        gobuster_threads_num =  str(config["threads"]["gobuster"])
        gobuster_wordlist_name = str(config["wordlists"]["gobuster"])
        
        proc = subprocess.Popen(f'gobuster dns -d {domain} -w {WORDLISTS_PATH}/{gobuster_wordlist_name} -t {gobuster_threads_num} -o  {parent_outdir}/temp/sub-gobuster-1.txt -z -q; cat {parent_outdir}/temp/sub-gobuster-1.txt | sed s/"Found: "/""/g > {parent_outdir}/temp/sub-gobuster-2.txt',shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()

        proc = subprocess.Popen(f'rm {parent_outdir}/temp/sub-gobuster-1.txt; mv {parent_outdir}/temp/sub-gobuster-2.txt {parent_outdir}/temp/sub-gobuster.txt',shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()

    

    # fetching all disovered subdomains from the different tools and sources and storing them in one file (sub-final-1.txt)
    # before starting the sort and filter process.
    for sub_res in temp_subdomain_files:

        proc = subprocess.Popen(f"cat {parent_outdir}/temp/sub-{sub_res}.txt >> {parent_outdir}/temp/sub-final-1.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()

    with open(f"{parent_outdir}/temp/sub-final-1.txt","r") as fr:

        
        line = str(fr.readline()).replace("\n","")

        with open(f"{parent_outdir}/temp/sub-final-2.txt","w") as fw:

            while len(line) > 0:
                
                # checking if the subdomain is in the execluded subdomains list.         
                if line in ex_subdomains:
                    pass

                elif is_wildcard_exculded(line,ex_wildcard_subdomains):
                    pass
                else:
                    fw.write(line+"\n")
                
                line = str(fr.readline()).replace("\n","")


    # removing duplicates and saving the results to (sub-final-3.txt) file.
    proc = subprocess.Popen(f"cat {parent_outdir}/temp/sub-final-2.txt | sort -u > {parent_outdir}/temp/sub-final-3.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

    # adding the included subdomains to to (sub-final-3.txt) file.
    
    if os.path.exists(f"{parent_outdir}/temp/sub-included.txt"):

        proc = subprocess.Popen(f"cat {parent_outdir}/temp/sub-included.txt | sort -u >> {parent_outdir}/temp/sub-final-3.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()

    # extracting active subdomains and saving the results to (subdomains.txt) file.
    proc = subprocess.Popen(f"cat {parent_outdir}/temp/sub-final-3.txt | dnsx -a -aaaa -cname -silent | sort -u > {parent_outdir}/subdomains.txt",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()




def web_discovery(parent_outdir,scan_config,input_file=None):

    # loading the tool config from yaml config file and building the command based on the options specified in the config file.

    httpx_config = scan_config["web_discovery"]

    if input_file is not None:
        httpx_input_file = input_file

    else:
        httpx_input_file = f"{parent_outdir}/subdomains.txt"

    httpx_command = f"cat {httpx_input_file} | httpx -silent -status-code -title -web-server -tech-detect -json"


    if "threads" in httpx_config:
        httpx_command+=f" -threads {str(httpx_config['threads'])}"
    
    if "retries" in httpx_config:
        httpx_command+=f" -retries {str(httpx_config['retries'])}"

    if "web_ports" in httpx_config:
        httpx_command+=f" -ports {str(httpx_config['web_ports'])}"
    
    if "timeout" in httpx_config:
        httpx_command+=f" -timeout {str(httpx_config['timeout'])}"
    
    if "rate_limit" in httpx_config:
        httpx_command+=f" -rate-limit {str(httpx_config['rate_limit'])}"
    
    httpx_command+=f" > {parent_outdir}/live_urls_info.json"

    # run httpx against the list of discovered subdomains.
    proc = subprocess.Popen(httpx_command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

    live_urls = []
    

    # parsing httpx raw json output (each line is a json object).  

    with open(f"{parent_outdir}/live_urls_info.json","r") as f:

        line = str(f.readline()).replace("\n","")
        

        while len(line) > 0:

            live_url = json.loads(line)
            live_urls.append(live_url)
            
            line = str(f.readline()).replace("\n","")
    


    live_urls = filter_live_urls(live_urls)



    # saving live urls after parsing the httpx json output.
    with open(f"{parent_outdir}/live_urls.txt","w") as f:

        for live_url in live_urls:

            f.write(str(live_url["url"])+"\n")

    return live_urls




