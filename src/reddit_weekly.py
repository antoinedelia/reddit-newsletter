# Given a list of subreddits, send an email containing the top posts from each of them every week

import base64
from datetime import datetime
import json
import logging
import os

import boto3
from botocore.exceptions import ClientError
import requests

from src.reddit import Post

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger()
log_level = logging.getLevelName(LOG_LEVEL)
logger.setLevel(log_level)
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

reddit_api_url = "https://oauth.reddit.com/r/{subreddit}/top.json?sort=top&t=week&limit={limit}"
default_subreddits = ["pics", "videos"]
if "SUBREDDITS" in os.environ:
    default_subreddits = os.getenv("SUBREDDITS").split(",")
POST_LIMIT = os.getenv("POST_LIMIT", 10)
USER_AGENT = os.getenv("USER_AGENT")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")


def lambda_handler(event, context):
    if not sender_mail or not recipients_mails:
        return format_response(400, "The sender or destination mail is not set.")
    mail_content = ""

    logger.info("Trying to get a new access token.")
    token_url = "https://www.reddit.com/api/v1/access_token"
    payload = "grant_type=client_credentials"
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(REDDIT_CLIENT_ID + ":" + REDDIT_CLIENT_SECRET)}"
    }
    response = requests.post(token_url, headers=headers, data=payload)
    if response.status_code != 200:
        return format_response(response.status_code, f"Failed to get access token ({response.status_code}) with error: {e}")
    access_token = response.json()["access_token"]
    logger.info(f"Successfully retrieved new access token!")

    for subreddit in default_subreddits:
        subreddit_url = reddit_api_url.format(subreddit=subreddit, limit=POST_LIMIT)
        mail_content += f"/r/{subreddit}:<br>"
        logger.info(f"Requesting url: {subreddit_url}")
        result = requests.get(subreddit_url, headers={"Authorization": f"Bearer {access_token}", "User-agent": USER_AGENT})
        if result.status_code != 200:
            logger.warning(f"Subreddit {subreddit} sent a {result.status_code} HTTP code.")
            mail_content += f"Could not get posts for subreddit /r/{subreddit} with HTTP code {result.status_code}.<br><br>"
            logger.warning(result.text)
            continue
        posts_json = result.json()["data"]["children"]
        posts = [Post(post) for post in posts_json]
        for post in posts:
            mail_content += f'<a href="{post.url}">{post.title}</a><br>'
        mail_content += "<br>"

    current_week_number = datetime.date(datetime.today()).isocalendar()[1]

    # Try to send the email
    try:
        # Provide the contents of the email
        logger.info(f"Sending mail to {recipients_mails}")
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
