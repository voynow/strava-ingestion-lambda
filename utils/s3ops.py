
import boto3
import json
import time

import utils.strava_api as strava_api
import utils.configs as configs


bucket_name = "strava-raw"
s3 = boto3.resource('s3')


def load_table(bucket, table):
    """ Get table from s3
    """
    obj = s3.Object(bucket, table)
    return json.loads(obj.get()['Body'].read())


def append_new_data(new_data, existing_data):
    """ Append new activities to activities table
    """
    for item in new_data[::-1]:
        key = str(item['id'])
        
        if key not in existing_data:
            item['api_call_ts'] = time.strftime(configs.strfrmt)
            existing_data[key] = item

    return existing_data



def update_activities(access_token):
    """ write activities to strava-raw s3 bucket
    """
    filename = "activities.json"

    activities_from_api = strava_api.get_activities(access_token)
    existing_activities = load_table(bucket_name, filename)
    master_activities = append_new_data(activities_from_api, existing_activities)
    master_ids = list(master_activities.keys())

    # s3.Object(bucket_name, filename).put(Body=json.dumps(master_activities))
    return master_ids


def update_tables(ids, access_token):
    """
    """
    bucket = "strava-raw"

    for table_name in configs.activities_endpoints:

        filename = f"{table_name}.json"
        table = load_table(bucket, filename)
        missing_ids = [i for i in ids if i not in table]

        new_data = []
        for idx, url in strava_api.get_urls(missing_ids, table_name):
            response = strava_api.get_request(access_token, url)
            if table_name == "laps":
                print(response)
                print()
            response['id'] = idx
            new_data.append(response)

        # master_table = append_new_data(new_data, table)
        # add new data to existing table
        # write table to s3
