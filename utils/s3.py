
import boto3
import json
import time

import utils.configs as configs


bucket_name = "strava-raw"
s3 = boto3.resource('s3')


def load_table(bucket, table):
    """ Get table from s3
    """
    obj = s3.Object(bucket, table)
    return json.loads(obj.get()['Body'].read())


def append_new_activities(new_activities, existing_activities):
    """ Append new activities to activities table
    """
    for activity in new_activities[::-1]:
        key = str(activity['id'])
        
        if key not in existing_activities:
            activity['api_call_ts'] = time.strftime(configs.strfrmt)
            existing_activities[key] = activity

    return existing_activities



def write_activities(new_activities):
    """ write activities to strava-raw s3 bucket
    """
    filename = "activities.json"
    existing_activities = load_table(bucket_name, filename)
    master_activities = append_new_activities(new_activities, existing_activities)
    s3.Object(bucket_name, filename).put(Body=json.dumps(master_activities))


