
import utils
import requests


def lambda_handler(event, context):
    
    oauth_url = utils.create_oauth_url()
    resp = requests.post(oauth_url)
    
    if resp.status_code == 200:
        auth_code = resp.json()['access_token']
        activities = utils.get_activities(auth_code)
        utils.write_activities(activities)
    else:
        raise Exception(f"Oauth request returning invalid status code: {resp.status_code}")
        
    return 1