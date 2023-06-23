# Given a list of subreddits, send an email containing the top posts from each of them every week

from src.reddit import Post
import requests
import os
from datetime import datetime
import boto3
import logging
import json
from botocore.exceptions import ClientError

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger()
log_level = logging.getLevelName(LOG_LEVEL)
logger.setLevel(log_level)
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s\n'))
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)


def format_response(status_code: int, message: str):
    if status_code >= 400:
        logger.error(message)
    else:
        logger.info(message)
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message}),
    }


###
# SMTP Configuration
###

sender_mail = os.getenv("SENDER_MAIL")
recipients_mails = os.getenv("RECIPIENTS_MAILS").split(",")
mail_object = "Reddit top posts - Week #{week_number}"
CHARSET = "UTF-8"
ses_client = boto3.client("ses")


###
# Reddit Configuration
###

reddit_api_url = "https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=week&limit={limit}"
default_subreddits = ["pics", "videos"]
if "SUBREDDITS" in os.environ:
    default_subreddits = os.getenv("SUBREDDITS").split(",")
POST_LIMIT = os.getenv("POST_LIMIT", 10)


def lambda_handler(event, context):
    if not sender_mail or not recipients_mails:
        return format_response(400, "The sender or destination mail is not set.")
    mail_content = ""
    for subreddit in default_subreddits:
        subreddit_url = reddit_api_url.format(subreddit=subreddit, limit=POST_LIMIT)
        result = requests.get(subreddit_url, headers={"User-agent": "your bot 0.1"})
        if result.status_code != 200:
            logger.warning(f"Subreddit {subreddit} sent a {result.status_code} HTTP code.")
            continue
        posts_json = result.json()["data"]["children"]
        posts = [Post(post) for post in posts_json]
        mail_content += f"/r/{subreddit}:<br>"
        for post in posts:
            mail_content += f'<a href="{post.url}">{post.title}</a><br>'
        mail_content += "<br>"

    current_week_number = datetime.date(datetime.today()).isocalendar()[1]

    # Try to send the email.
    try:
        # Provide the contents of the email.
        ses_client.send_email(
            Destination={
                "ToAddresses": recipients_mails,
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": mail_content,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": mail_object.format(week_number=current_week_number),
                },
            },
            Source=sender_mail,
        )
    except ClientError as e:
        return format_response(500, e.response["Error"]["Message"])
    else:
        recipients = ", ".join(recipients_mails)
        return format_response(200, f"Mail successfully sent to {recipients}!")
