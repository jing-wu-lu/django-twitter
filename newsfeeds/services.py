from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        # wrong method
        # don't use for + query, very inefficient
        # use bulk_create, insert into db at the same time
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)

