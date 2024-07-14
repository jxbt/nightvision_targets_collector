import re
import json
import yaml


def is_wildcard_exculded(subdomain,ex_wildcard_subdomains):

    for regex_str in ex_wildcard_subdomains:

        m = re.compile(regex_str).fullmatch(subdomain)

        if m != None:
            return True
        else:
            pass
    
    return False



def filter_live_urls(live_urls):

    live_urls_old = live_urls
    live_urls_new = []

    for live_url_1 in live_urls_old:
        
        if str(live_url_1["port"]) == "443" and live_url_1["scheme"] == "https":

            https_443_live_url = live_url_1
            https_443_live_url["url"] = str(https_443_live_url["url"]).replace(":443","")

            
            live_urls_new.append(https_443_live_url)


            for live_url_2 in live_urls_old:
                
                
                if live_url_2["input"] == https_443_live_url["input"] and str(live_url_2["port"]) == "80" and live_url_2["scheme"] == "http":

                    http_80_live_url = live_url_2
                    http_80_live_url["url"] = str(http_80_live_url["url"]).replace(":80","")



                    if ("location" in http_80_live_url) and (http_80_live_url["location"][0:len(https_443_live_url["url"])] == https_443_live_url["url"]):
                        
                        if http_80_live_url in live_urls_new:
                            live_urls_new.remove(http_80_live_url)

                    else:
                        live_urls_new.append(http_80_live_url)

                    live_urls_old.remove(live_url_2)

        elif str(live_url_1["port"]) == "80" and live_url_1["scheme"] == "http":

                http_80_live_url = live_url_1
                http_80_live_url["url"] = str(http_80_live_url["url"]).replace(":80","")

                
                live_urls_new.append(http_80_live_url)
        else:
            live_urls_new.append(live_url_1)
    
    return live_urls_new



# the "load_conf" function is used to load the configuration file.
def load_conf(config_file_path):

    conf = {}
    config_file_format = "json"
    
    # checking the configuration file is written in yaml (the default is JSON).
    if config_file_path[-5:] == ".yaml" or config_file_path[-4:] == ".yml":
        config_file_format = "yaml"
    else:
        pass
    
    # loading the file.
    with open(config_file_path,"r") as f:

        if config_file_format == "json":
            conf = json.load(f)
        elif config_file_format == "yaml":
            conf = yaml.safe_load(f)
        else:
            pass
    
    # return the configuration as an object.
    return conf