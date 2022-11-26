
import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from headless_chrome import create_driver

import utils.s3 as s3
import utils.configs as configs

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


def activities_driver():

    oauth_url = s3.create_oauth_url()
    resp = requests.post(oauth_url)

    if resp.status_code == 200:
        auth_code = resp.json()['access_token']
        return s3.get_activities(auth_code)
    else:
        raise Exception(f"Oauth request returning invalid status code: {resp.status_code}")