def invalidate_following_cache(sender, instance, **kwargs):
    # 基本是都是创建造成的，如果不是，还有一个create 参数可以加上
    # 引用写在外面会造成循环引用的报错
    # 在运行的时候，已经存在了就不会有影响
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)

