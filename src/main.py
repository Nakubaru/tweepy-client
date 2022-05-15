import sys

from lib import TwitterClient


def main():
    keyword = sys.argv[1]

    twitter = TwitterClient()
    tweets = twitter.get_searched_tweets(keyword=keyword,
                                         exclude_retweets=True,
                                         count=100)

    from pprint import pprint
    pprint(tweets)


if __name__ == '__main__':
    main()
