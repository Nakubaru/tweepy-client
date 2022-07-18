import logging
import sys

from lib import MySQLClient, TwitterClient

logging.basicConfig(
    format='[%(asctime)s][%(name)s::%(levelname)s] %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

COLUMNS = [
    'tweet_id',
    'account_id',
    'account_name',
    'username',
    'tweet',
    'favorites',
    'retweets',
    'searched_at',
    'tweeted_at'
]


def insert_tweets(client: MySQLClient, tweets: list) -> None:
    data = [tuple(tweet[col] for col in COLUMNS) for tweet in tweets]

    client.executemany(f"""
    INSERT INTO tweets ({','.join(COLUMNS)})
    VALUES ({','.join('%s' for _ in range(len(COLUMNS)))})
    ON DUPLICATE KEY UPDATE
    {','.join([f'{col} = VALUES({col})' for col in COLUMNS])}
    """, data)

    logger.info('tweets inserted.')


def main():
    keyword = sys.argv[1]

    twitter = TwitterClient()
    tweets = twitter.get_searched_tweets(keyword=keyword,
                                         exclude_retweets=True,
                                         count=100)

    mysql = MySQLClient(database='tweet')
    insert_tweets(client=mysql, tweets=tweets)


if __name__ == '__main__':
    main()
