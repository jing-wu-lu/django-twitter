from dateutil import parser
from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class EndlessPagination(BasePagination):
    page_size = 20

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def to_html(self):
        pass

    def paginate_ordered_list(self, reverse_ordered_list, request):
        if 'created_at__gt' in request.query_params:
            # 2021-11-11 00:00:00.123456
            created_at__gt = parser.isoparse(request.query_params['created_at__gt'])
            objects = []
            for obj in reverse_ordered_list:
                if obj.created_at > created_at__gt:
                    objects.append(obj)
                else:
                    break
            self.has_next_page = False
            return objects

        index = 0
        if 'created_at__lt' in request.query_params:
            created_at__lt = parser.isoparse(request.query_params['created_at__lt'])
            for index, obj in enumerate(reverse_ordered_list):
                if obj.created_at < created_at__lt:
                    break
            else:
                # 没找到任何满足条件的 objects， 返回空数组
                # 注意这个 else 对应的是 for， 参见 python 的 for else 语法
                reverse_ordered_list = []
        self.has_next_page = len(reverse_ordered_list) > index + self.page_size
        return reverse_ordered_list[index: index + self.page_size]

    def paginate_queryset(self, queryset, request, view=None):
        if type(queryset) == list:
            return self.paginate_ordered_list(queryset, request)

        if 'created_at__gt' in request.query_params:
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            return queryset.order_by('-created_at')

        if 'created_at__lt' in request.query_params:
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]

    def get_paginated_response(self, data):
        return Response({
            'has_next_page': self.has_next_page,
            'results': data,
        })
