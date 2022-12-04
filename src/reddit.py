from datetime import datetime
from dateutil import tz

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

reddit_base_url = "https://www.reddit.com"


class Post(object):
    def __init__(self, post_json):
        self.title = post_json["data"]["title"]
        self.author = post_json["data"]["author"]
        self.number_comments = post_json["data"]["num_comments"]
        self.karma = post_json["data"]["score"]
        self.url = reddit_base_url + post_json["data"]["permalink"]
        self.external_url = post_json["data"]["url"]
        self.is_nsfw = post_json["data"]["over_18"]
        self.is_spoiler = post_json["data"]["spoiler"]

        datetime_utc = datetime.utcfromtimestamp(post_json["data"]["created_utc"]).replace(tzinfo=from_zone)
        self.creation_datetime = datetime_utc.astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
