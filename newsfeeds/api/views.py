from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # self define queryset, because need permission to view newsfeeds
        # only view the current logged in user's newsfeed
        # also can be self.request.user.newsfeed_set.all()
        # it is the best to write as NewsFeed.objects.filter(user=self.request.user)
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        serializer = NewsFeedSerializer(self.get_queryset(), many=True)
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)
