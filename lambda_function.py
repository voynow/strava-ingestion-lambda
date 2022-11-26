
import utils.s3 as s3
import utils.strava_api as strava_api


def lambda_handler(event, context):

    activities = strava_api.activities_driver()
    s3.write_activities(activities)

    return 1
