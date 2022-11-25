
import boto3
import configs
import json
import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException      
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from headless_chrome import create_driver


strfrmt = "%m/%d/%Y, %H:%M:%S"
bucket_name = "strava-raw"
s3 = boto3.resource('s3')


def get_code_from_strava():
    """
    Selenium code to automate access to account authorization for API
    Storing code from URL in configs file, this code is required for oauth API call
    """
    driver = create_driver()
    driver.get(configs.get_oauth_code_param())

    driver.find_element(By.CSS_SELECTOR, f'input#email').send_keys(configs.email)
    driver.find_element(By.CSS_SELECTOR, f'input#password').send_keys(configs.password + Keys.ENTER)

    driver.find_element(By.CLASS_NAME, "btn-primary").click()

    for param in driver.current_url.split("&"):
            if "code" in param:
                    code = param.split("=")[1]
    driver.quit()

    return code


def create_oauth_url():
    """
    Constrct oauth url from configuration data
    """
    code = get_code_from_strava()
    url_data = configs.get_oauth_url(code)
    url_string = url_data['url']

    for k, v in url_data['params'].items():
        url_string += f'{k}={v}&'
    return url_string


def get_activities_url(access_token):
    return {
        "url": "https://www.strava.com/api/v3/athlete/activities",
        "params": {
            "header": {'Authorization': 'Bearer ' + access_token},
            "param": {'per_page': 50, 'page': 1}
        }
    }


def get_activities(access_token):
    """
    Get activity data using access token from oauth API call
    """
    activities_url = get_activities_url(access_token)

    return requests.get(
        activities_url['url'], 
        headers=activities_url['params']['header'], 
        params=activities_url['params']['param']
    ).json()


def strava_raw_ls():
    """
    return list of all files within the strava-raw s3 bucket
    """
    objs = s3.Bucket(bucket_name).objects.all()
    
    return [obj.key for obj in objs]
    
    
def write_to_s3(activity, filename):
    """
    Dump json to strava-raw s3 bucket
    """
    object = s3.Object(bucket_name, filename)
    object.put(Body=json.dumps(activity))


def write_activities(activities):
    """
    write activities to strava-raw s3 bucket
    """
    existing_activities = strava_raw_ls()

    for activity in activities:

        # create filename from activity id
        filename = str(activity['id']) + ".json"
    
        # save json if file does not exist
        if filename not in existing_activities:
            activity['api_call_ts'] = time.strftime(strfrmt)
            write_to_s3(activity, filename)
