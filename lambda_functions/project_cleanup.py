import ast
import boto3
import urllib.parse

s3 = boto3.client('s3')


def lambda_handler(event, context):
    """
    This lambda function handle cleanup processes when a project is deleted
        1. Delete files from S3 bucket after project is removed from database

    :param event:
    :param context:
    :return:
    """

    # { "event_name": <string>, "data": <dict>}
    event_message = ast.literal_eval(event['Records'][0]['Sns']['Message'])

    print(event_message)

    if event_message["event_type"] == "PROJECT_CLEANUP":
        """
            {"data": {"bucket_name": <string>, "project_key": <string>}
        """
        event_data = event_message["data"]

        bucket_name = event_data["bucket_name"]
        project_key = event_data["project_key"]

        if bucket_name and project_key:
            parsed_project_key = urllib.parse.unquote_plus(project_key, encoding='utf-8')

            print(parsed_project_key)

            try:
                # delete s3 object or set delete marker on versioned object
                s3.delete_object(
                    Bucket=bucket_name,
                    Key=parsed_project_key,
                )

                return "Cleanup Complete ({})".format(parsed_project_key)
            except Exception as e:
                print(e)
                print('Error handling cleanup for project - {}'.format(parsed_project_key))
                raise e
