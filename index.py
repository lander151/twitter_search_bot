import logging
from operator import itemgetter

import time
import tweepy
from datetime import datetime, timedelta, date
from config import TWITTER_KEYS
from collections import OrderedDict

class PostTwitter:

    def __init__(self):
        self.access_token = TWITTER_KEYS.get('access_token')
        self.access_token_secret = TWITTER_KEYS.get('access_token_secret')
        self.consumer_key = TWITTER_KEYS.get('consumer_key')
        self.consumer_secret = TWITTER_KEYS.get('consumer_secret_key')

        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)

    @staticmethod
    def get_string_date(date_to_convert):
        return date_to_convert.strftime("%Y-%m-%d")

    def get_dates_ranges(self):
        today = date.today()
        today_str = self.get_string_date(today)
        yesterday = today - timedelta(days=7)
        yesterday_str = self.get_string_date(yesterday)

        return yesterday_str, today_str

    def get_tweets(self, search_text):
        results = list()

        dates = self.get_dates_ranges()
        text = '%s since:%s until:%s -filter:retweets' % (search_text, dates[0], dates[1])
        geo = '40.3026029,-7.1186802,750km'

        for tweets in tweepy.Cursor(self.api.search, q=text, count=100, results_type='recent', geocode=geo,
                                    tweet_mode='extended').pages():
            results += tweets
        rate_limit = self.api.rate_limit_status()
        if rate_limit['resources']['search']['/search/tweets'].get('remaining') < 1:
            ts = time.time()
            reset_time = rate_limit['resources']['search']['/search/tweets'].get('reset')
            print(ts)
            print(reset_time)
            time.sleep(reset_time - ts)
        return results

    def post_tweet(self, list_tweets, yesterday_date, search_text):
        arroba = list_tweets[0]['user']
        lenght = list_tweets[0]['len']
        text = '@%s nombró ayer día %s %s veces a "%s"' % (arroba,  yesterday_date, lenght, search_text)

        # self.api.update_status(text)
        print(text)

    def get_ranking(self, tweets):
        ranking_dict = dict()
        ranking_list = list()

        for tweet in tweets:
            ranking = {
                'user': None,
                'user_id': None,
                'tweets': [],
                'len': 0
                       }
            user_id = tweet.user.id
            user_name = tweet.user.screen_name

            tweet_id = tweet.id
            tweet_text = tweet.full_text
            tweet = {'id': tweet_id, 'text': tweet_text}

            if user_id in ranking_dict:
                ranking = ranking_dict[user_id]

            ranking['user'] = user_name
            ranking['user_id'] = user_id
            ranking['tweets'].append(tweet)
            ranking['len'] = len(ranking['tweets'])
            ranking_dict[user_id] = ranking

        for key, value in ranking_dict.items():
            ranking_list.append(value)

        listsorted = sorted(ranking_list, key=itemgetter('len'), reverse=True)

        return listsorted


tw = PostTwitter()

results = tw.get_tweets('eta')

ordered_list = tw.get_ranking(results)

today = date.today() - timedelta(days=1)
yesterday_str = today.strftime("%Y-%m-%d")


tw.post_tweet(ordered_list, yesterday_str, 'eta')
