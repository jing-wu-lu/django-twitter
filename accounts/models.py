from accounts.listeners import user_changed, profile_changed
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete


class UserProfile(models.Model):
    # OneToOne field 会创建一个 unique index, 确保不会有多个 UserProfile 指向同一个 user
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # Django 还有一个 ImageField, 但是尽量不要用，会有很多其它的问题，用 FileFiled 可以起到
    # 同样的效果。因为我们最后都是以文件形式存储起来，使用的是文件的 url 进行访问
    avatar = models.FileField(null=True)
    # 当一个 user 被创建起立之后，会创建一个 user profile 的 object
    # 此时 用户还来不及设置 nickname 等信息，因此设置 null=True
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# 定义一个 profile 的 property 的方法，植入到 User 的这个 model 里
# 这样当我们通过 user 的一个实例化对象访问 profile 的时候，即 user_instance.profile
# 就会在 userProfile 中进行 get_or_create 来获得对应的 profile 的 object
# 这种写法实际上是一个利用 python 的灵活性进行 hack 的方法，这样会方便我们通过 user 快速
# 访问到对应的 profile 信息

def get_profile(user):
    # 内部引用避免循环引用的报错
    from accounts.services import UserService
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    # 从数据库取
    # profile, _ = UserProfile.objects.get_or_create(user=user)
    # 从缓存取
    profile = UserService.get_profile_through_cache(user.id)
    # 使用 user 对象的属性进行缓存（cache), 避免多次调用同一个 user 的 profile 时，
    # 重复的对数据库进行查询
    setattr(user, '_cached_user_profile', profile)
    return profile


# 给 User Model 增加了一个 profile 的 property 方法用于快捷访问
User.profile = property(get_profile)


# hook up with listeners to invalidate cache
pre_delete.connect(user_changed, sender=User)
post_save.connect(user_changed, sender=User)

pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)
