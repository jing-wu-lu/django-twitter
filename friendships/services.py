from django.conf import settings
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN
from gatekeeper.models import GateKeeper
from friendships.hbase_models import HBaseFollowing, HBaseFollower
import time

cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    # @classmethod
    # def has_followed(cls, from_user, to_user):
    #     return Friendship.objects.filter(
    #         from_user=from_user,
    #         to_user=to_user,
    #     ).exists()
    @classmethod
    def get_follower_ids(cls, to_user_id):
        friendships = Friendship.objects.filter(to_user_id=to_user_id)
        return [friendship.from_user_id for friendship in friendships]

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        # LRU Least Recently Used
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])
        cache.set(key, user_id_set)
        return user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        # 为了更好地保持数据一致性，当 key 有更新的时候，从 cache 中删除记录 而不是去更新
        # 删除带来的不一致性远远低于更新带来的不一致性
        # 常驻内存的，比如某明星的，就不轻易删掉，有另一套机制
        # web 中通常不会加锁，多线程造成的数据一致性问题是不可避免的
        # 比如刚取完数据，数据库被更新了
        # 因为web 和 memcached 的服务器通常在不同的机器上
        # 如果加分布式锁，会造成访问效率很差，可能比直接访问数据库的速度还慢
        # 解决办法是通过 time out 的机制，即使有不一致，很快就可以更新
        # 不适用于金融系统，强一致性是重点
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)

    @classmethod
    def follow(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return None

        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            # create data in mysql
            return Friendship.objects.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            )

        # create data in hbase
        now = int(time.time() * 1000000)
        HBaseFollower.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now,
        )
        return HBaseFollowing.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now,
        )
