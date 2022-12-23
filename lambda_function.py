
import utils.s3ops as s3ops
import utils.strava_api as strava_api


def lambda_handler(event, context):

    activities = strava_api.activities_driver()
    new_activity_ids = s3ops.update_activities(activities)
    activity_details_urls = strava_api.get_api_requests(new_activity_ids)
    s3ops.update_tables(activity_details_urls)

    return 1
