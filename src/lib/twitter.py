import datetime
import os
from typing import List, Union

import tweepy
from pytz import timezone

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIMEZONE = 'Asia/Tokyo'


class TwitterClient(object):
    _RESULT_RECENT = 'recent'
    _RESULT_POPULAR = 'popular'
    _FULL_TEXT = 'extended'

    def __init__(self,
                 bearer_token: str = None,
                 consumer_key: str = None,
                 consumer_secret: str = None,
                 access_token: str = None,
                 access_token_secret: str = None,
                 wait_on_rate_limit: bool = True) -> None:
        self._bearer_token = \
            bearer_token or os.getenv('BEARER_TOKEN')
        self._consumer_key = \
            consumer_key or os.getenv('CONSUMER_KEY')
        self._consumer_secret = \
            consumer_secret or os.getenv('CONSUMER_SECRET')
        self._access_token = \
            access_token or os.getenv('ACCESS_TOKEN')
        self._access_token_secret = \
            access_token_secret or os.getenv('ACCESS_TOKEN_SECRET')
        # self._create_client()
        self._create_api(wait_on_rate_limit=wait_on_rate_limit)

    def _create_client(self) -> None:
        try:
            self._client = tweepy.Client(
                bearer_token=self._bearer_token,
                consumer_key=self._consumer_key,
                consumer_secret=self._consumer_secret,
                access_token=self._access_token,
                access_token_secret=self._access_token_secret
            )
        except Exception:
            raise

    def _create_api(self, wait_on_rate_limit: bool = True) -> None:
        try:
            self._auth = \
                tweepy.OAuthHandler(consumer_key=self._consumer_key,
                                    consumer_secret=self._consumer_secret)
            self._auth.set_access_token(key=self._access_token,
                                        secret=self._access_token_secret)
            self._api = tweepy.API(self._auth,
                                   wait_on_rate_limit=wait_on_rate_limit)
        except Exception:
            raise

    @staticmethod
    def _get_query(keyword: Union[str, List[str]],
                   min_faves: int,
                   min_retweets: int,
                   exclude_retweets: bool,
                   filter_media: bool) -> str:
        _exclude_retweets = 'exclude:retweets' if exclude_retweets else ''
        _filter_media = 'filter:media' if filter_media else ''

        if isinstance(keyword, str):
            _keyword = f'#{keyword} OR {keyword}'
        elif isinstance(keyword, list):
            _keyword = ' AND '.join([f'(#{k} OR {k})' for k in keyword])
        else:
            raise Exception(f'invalid keyword(s): {keyword}')

        return f'{_keyword} {_exclude_retweets} {_filter_media}' \
               f'min_faves:{min_faves} min_retweets:{min_retweets}'

    @staticmethod
    def _datetime_to_jst_str(dt: datetime.datetime) -> str:
        return dt.astimezone(timezone(TIMEZONE)).strftime(DATETIME_FORMAT)

    @classmethod
    def _tweet_summarize(cls,
                         tweets: Union[tweepy.models.ResultSet,
                                       tweepy.models.SearchResults]) -> list:
        searched_at = datetime.datetime.now().strftime(DATETIME_FORMAT)

        return [
            dict(
                tweet_id=tweet.id,
                tweeted_at=cls._datetime_to_jst_str(dt=tweet.created_at),
                account_id=tweet.user.id,
                username=tweet.user.name,
                account_name=tweet.user.screen_name,
                tweet=tweet.text
                if hasattr(tweet, 'text') else tweet.full_text,
                favorites=tweet.favorite_count,
                retweets=tweet.retweet_count,
                searched_at=searched_at
            )
            for tweet in tweets
        ]

    def get_searched_tweets(self,
                            keyword: Union[str, List[str]],
                            min_faves: int = 0,
                            min_retweets: int = 0,
                            exclude_retweets: bool = False,
                            filter_media: bool = False,
                            count: int = 10) -> list:
        query = self._get_query(keyword=keyword,
                                min_faves=min_faves,
                                min_retweets=min_retweets,
                                exclude_retweets=exclude_retweets,
                                filter_media=filter_media)

        try:
            tweets = self._api.search_tweets(q=query,
                                             count=count,
                                             result_type=self._RESULT_RECENT,
                                             tweet_mode=self._FULL_TEXT,
                                             include_entities=True)
            return self._tweet_summarize(tweets=tweets)

        except Exception:
            raise

    def get_home_timeline(self, count: int = 10) -> list:
        try:
            tweets = self._api.home_timeline(count=count)
            return self._tweet_summarize(tweets=tweets)
        except Exception:
            raise

    def get_user_timeline(self, account_name: str, count: int = 10) -> list:
        try:
            tweets = self._api.user_timeline(user_id=account_name, count=count)
            return self._tweet_summarize(tweets=tweets)
        except Exception:
            raise
