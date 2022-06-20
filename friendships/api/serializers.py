from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FollowingUserIdSetMixin:
    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return {}
        # 缓存是存在进程中的，当一个HTTP 请求过来，返回之后，这个内存就会被释放掉
        # 存在 memcached 中的在进程结束之后也不会被释放掉
        # memcached 释放主要有3个原因：超时，主动删除，内存不够用而且key的访问频率不够高(LRU 淘汰机制)
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id,
        )
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set


# 可以通过 source = xxx 指定去访问每个model instance 的 xxx 方法
# 即 model_instance.xxx 来获取数据
#  https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly


class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_from_user')
    has_followed = serializers.SerializerMethodField()
    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        # if self.context['request'].user.is_anonymous:
        #     return False
        # # <TODO> 这个部分会对每个 object 都去执行一次 SQL 查询， 速度会很慢，如何优化呢？
        # return FriendshipService.has_followed(self.context['request'].user, obj.from_user)
        return obj.from_user_id in self.following_user_id_set


class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        # if self.context['request'].user.is_anonymous:
        #     return False
        # return FriendshipService.has_followed(self.context['request'].user, obj.to_user)
        return obj.to_user_id in self.following_user_id_set


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You cannot follow yourself.',
            })
        # if not User.objects.filter(id=attrs['to_user_id']).exists():
        #     raise ValidationError({
        #         'message': 'You can not follow a non-exist user.'
        #     })
        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user_id=attrs['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'You have already followed the user.',
            })
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )
