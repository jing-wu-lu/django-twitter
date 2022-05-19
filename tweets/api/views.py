from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService


class TweetViewSet(viewsets.GenericViewSet):
    # queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        # self.get_queryset()
        """reload list method, does not show all the tweets,
        must have selected user_id as the screening condition."""
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)
        # this query is translated into
        # select * from twitter_tweets
        # where user_id= xxx
        # order by created_at desc
        # this sql query uses composite index of user and created_at
        # only user as index is not enough
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        # conventionaly, response uses JSON with hash format, not list format
        return Response({'tweets': serializer.data})

    def create(self, request):
        """reload create method, default current logged in user as tweet.user"""
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input.",
                'errors': serializer.errors,
            }, status=400)
        # save() will call create method in TweetSerializerForCreate
        # return a django ORM object
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)
    # TweetSerializerForCreate is for tweet creation, kind of deserialize from the giving hash data
    # TweetSerializer is for tweet display
