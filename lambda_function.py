
import utils.s3ops as s3ops
import utils.strava_api as strava_api


def lambda_handler(event, context):

    activities = strava_api.activities_driver()
    s3ops.write_activities(activities)

    return 1
