from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from newsfeeds.api.serializers import NewsFeedSerializer
from utils.paginations import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def get_queryset(self):
        # self define queryset, because need permission to view newsfeeds
        # only view the current logged-in user's newsfeed
        # also can be self.request.user.newsfeed_set.all()
        # it is the best to write as NewsFeed.objects.filter(user=self.request.user)
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        # serializer = NewsFeedSerializer(
        #     self.get_queryset(),
        #     context={'request': request},
        #     many=True,
        # )
        # return Response({
        #     'newsfeeds': serializer.data,
        # }, status=status.HTTP_200_OK)
        # queryset = NewsFeedService.get_cached_newsfeeds(request.user.id)
        # page = self.paginate_queryset(queryset)
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        # page 是 None 代表现在请求的数据可能不在 cache 里，需要直接去 db 来获取
        if page is None:
            queryset = NewsFeed.objects.filter(user=request.user)
            page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
