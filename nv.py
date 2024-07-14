import requests
import json
import threading

def get_projects(nightvision_token):

    projects = []

    url = "https://api.nightvision.net/api/v1/projects/?own_projects=false&shared_projects=false"

    headers = {
        "accept": "application/json",
        "Authorization": f"token {nightvision_token}"
    }
    

    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:

        projects = json.loads(resp.text)["results"]

    

    return projects


def create_target(target,nightvision_token):


    url = "https://api.nightvision.net/api/v1/targets/url/"

    payload = [
        target
    ]
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"token {nightvision_token}"
    }

    resp = requests.post(url, json=payload, headers=headers,timeout=20)


    if resp.status_code == 201:
        pass


    
def create_targets(targets_lst,nightvision_token,project_id = None,project_name= None):

    targets_project_id = None

    if project_id is not None:
        targets_project_id = project_id
    

    all_projects = get_projects(nightvision_token)


    if len(all_projects) > 0:

        if project_name is not None:
            
            for p in all_projects:

                if p["name"] == project_name:
                    targets_project_id = p["id"]
                    break

        elif project_id is None:
            targets_project_id = all_projects[0]['id']

   

    targets_to_create = [
        
    ]

    for target in targets_lst:
        
        target_url = target["url"]
        target_name = f"{target['scheme']}_{target['input']}_{target['port']}"
        target_obj = {
            "is_active": True,
            "project": f"{targets_project_id}",
            "name": f"{target_name.replace('.','_')}",
            "location": f"{target_url}"
        }
    
        targets_to_create.append(target_obj)



    threads_num = 10
    i = 0

    while i < len(targets_to_create):

        threads = []

        for _ in range(threads_num):
            if i < len(targets_to_create):
                t = threading.Thread(target=create_target, args=[targets_to_create[i], nightvision_token])
                t.start()
                threads.append(t)
                i += 1
            else:
                break

        for thread in threads:
            thread.join()