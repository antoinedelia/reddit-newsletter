# Given a list of subreddits, send an email containing the top posts from each of them every week

from src.reddit import Post
import requests
import os
from datetime import datetime
import boto3
import logging
import json
from botocore.exceptions import ClientError

logger = logging.getLogger()


def return_response(status_code: int, message: str):
    if status_code >= 400:
        logger.error(message)
    else:
        logger.info(message)
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            "message": message
        })
    }


###
# SMTP Configuration
###

sender_mail = os.getenv('SENDER_MAIL')
destination_mail = os.getenv('DESTINATION_MAIL')
mail_object = 'Reddit top posts - Week #{week_number}'
CHARSET = "UTF-8"
ses_client = boto3.client('ses')


###
# Reddit Configuration
###

reddit_api_url = 'https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=week&limit={limit}'
list_subreddits = [
    'Android',
    'anime',
    'EDM',
    'france',
    'Games',
    'movies',
    'NintendoSwitch',
    'television',
    'videos'
]
POST_LIMIT = os.getenv('POST_LIMIT', 10)


def lambda_handler(event, context):
    if not sender_mail or not destination_mail:
        return return_response(400, 'The sender or destination mail is not set.')
    mail_content = ''
    for subreddit in list_subreddits:
        subreddit_url = reddit_api_url.format(subreddit=subreddit, limit=POST_LIMIT)
        result = requests.get(subreddit_url, headers={'User-agent': 'your bot 0.1'}).json()
        posts_json = result['data']['children']
        posts = [Post(post) for post in posts_json]
        mail_content += f'/r/{subreddit}:<br>'
        for post in posts:
            mail_content += f'<a href="{post.url}">{post.title}</a><br>'
        mail_content += '<br>'

    current_week_number = datetime.date(datetime.today()).isocalendar()[1]

    # Try to send the email.
    try:
        # Provide the contents of the email.
        ses_client.send_email(
            Destination={
                'ToAddresses': [
                    destination_mail,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': mail_content,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': mail_object.format(week_number=current_week_number),
                },
            },
            Source=destination_mail,
        )
    except ClientError as e:
        return return_response(500, e.response['Error']['Message'])
    else:
        return return_response(200, f'Mail successfully sent to {sender_mail}!')
