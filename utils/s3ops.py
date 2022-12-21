
import boto3
import json
import time

strfrmt = "%m/%d/%Y, %H:%M:%S"
bucket_name = "strava-raw"
s3 = boto3.resource('s3')


def write_activities(activities):
    """
    write activities to strava-raw s3 bucket
    """
    objs = s3.Bucket(bucket_name).objects.all()
    existing_activities = [obj.key for obj in objs]

    for activity in activities:

        # create filename from activity id
        filename = str(activity['id']) + ".json"
    
        # save json if file does not exist
        if filename not in existing_activities:
            activity['api_call_ts'] = time.strftime(strfrmt)
            s3.Object(bucket_name, filename).put(Body=json.dumps(activity))
