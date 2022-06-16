from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (TweetSerializer,
                                    TweetSerializerForCreate,
                                    TweetSerializerForDetail,
                                    )
from tweets.models import Tweet
from utils.decorators import required_params
from utils.paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet):
    # queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    # POST /api/tweets/ -> create
    # GET /api/tweets/?tweet_id=1 -> list
    # GET /api/tweets/1/ -> retrieve

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_params(params=['user_id'])
    def list(self, request):
        # GET request.query_params
        # POST request.data
        # self.get_queryset()
        """reload list method, does not show all the tweets,
        must have selected user_id as the screening condition."""
        # if 'user_id' not in request.query_params:
        #     return Response('missing user_id', status=400)
        # this query is translated into
        # select * from twitter_tweets
        # where user_id= xxx
        # order by created_at desc
        # this sql query uses composite index of user and created_at
        # only user as index is not enough
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        tweets = self.paginate_queryset(tweets)
        serializer = TweetSerializer(tweets,
                                     context={'request': request},
                                     many=True,)
        # conventionally, response uses JSON with hash format, not list format
        # return Response({'tweets': serializer.data})
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # <Homework> 通过某个query 参数 with_all_comments 来决定是否需要带上所有 comments
        # <Homework2> 通过某个 query 参数 with_preview_comments 来决定是否需要带上前三条 comments
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(
            tweet,
            context={'request': request},
        )
        return Response(serializer.data)

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
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=201,
        )
    # TweetSerializerForCreate is for tweet creation, kind of deserialize from the giving hash data
    # TweetSerializer is for tweet display
