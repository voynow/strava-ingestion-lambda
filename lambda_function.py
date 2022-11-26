
import s3_utils
import strava_api_utils


def lambda_handler(event, context):

    activities = strava_api_utils.activities_driver()
    # s3_utils.write_activities(activities)

    return 1
