
import boto3
import json
import time

strfrmt = "%m/%d/%Y, %H:%M:%S"
bucket_name = "strava-raw"
s3 = boto3.resource('s3')


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
