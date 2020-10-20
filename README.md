# Reddit Newsletter

Simple Lambda that send you a mail of the weekly top posts from Reddit every week.

## Prerequisites

You should have serverless and pip installed on your computer.

Also, be sure that the email address used to send the mail is verified in AWS SES. 

## Configuration

You can configure some parameters directly into the `serverless.yml` file:

- **SENDER_MAIL:** The sender of the mail. Must be verified in AWS SES. Required.
- **RECIPIENTS_MAILS:** The recipient of the mail. Can be a list by separating values with commas. Required.
- **SUBREDDITS:** The list of subreddits you want the script to check, must be separated by a comma. Optional (default: pics,videos).
- **POST_LIMIT:** The number of posts for each subreddit you want to send. Optional (default: 10).

## Deployment

```console
$ pip install -r requirements.txt

$ sls plugin install -n serverless-python-requirements

$ sls deploy
```