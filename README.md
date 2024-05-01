# Reddit Newsletter

Simple Lambda that sends you an email of the weekly top posts from Reddit every week.

- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

You should have the [Serverless Framework](https://www.serverless.com/) and `pip` installed on your machine.

Also, be sure that the email address used to send the mail is verified in AWS SES. 
The mails for the recipients also have to be verified if you are in AWS SES sandbox (see [Troubleshooting](#troubleshooting)).

For Reddit, you will need to [create a new Script App](https://www.reddit.com/prefs/apps/). This will give you a `client_id` and a `client_secret`, which are required.

## Configuration

You can configure some parameters directly into the `serverless.yml` file:

- **SENDER_MAIL:** The sender of the mail. Must be verified in AWS SES. Required.
- **RECIPIENTS_MAILS:** The recipient of the mail. Can be a list by separating values with commas. Required.
- **USER_AGENT:** The User-Agent that will be used in the headers when reaching Reddit. Required.
- **REDDIT_CLIENT_ID:** The client id of your Reddit app. Required.
- **REDDIT_CLIENT_SECRET:** The client secret of your Reddit app. Required.
- **SUBREDDITS:** The list of subreddits you want the script to check, must be separated by a comma. Optional (default: pics,videos).
- **POST_LIMIT:** The number of posts for each subreddit you want to send. Optional (default: 10).

## Deployment

```sh
pip install -r requirements.txt
serverless plugin install -n serverless-python-requirements
serverless deploy
```

## Troubleshooting

You might not be able to send mails if your recipient is not verified in AWS SES. This is because you are still in the AWS SES sandbox, and AWS is preventing you from sending mails to unknown addresses.

To get out of the AWS SES sandbox, please refer to the following documentation: https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html