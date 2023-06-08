from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from events.models import Event
from events.permissons import CustomPermission
from events.serializers import (
    EventCreateSerializer,
    EventSerializer,
    EventListSerializer,
    EventEditSerializer,
)


# Create your views here.
class EventView(generics.ListCreateAPIView):
    """EventView
    GET:
    행사정보 전체를 볼 수 있습니다.
    generics를 사용하여, GET요청은  queryse사용하여, 따로 만들지 않았습니다.

    POST:
    행사정보를 생성할 수 있습니다.
    permissions를 이용하여, admin만 행사정보를 생성할 수 있습니다
    단, 읽기권한은 모두에게 주어, 누구나 읽을 수 있습니다.
    작성에 성공할 시, 작성완료 메시지를 출력합니다.
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        CustomPermission,
    ]
    serializer_class = EventListSerializer
    queryset = Event.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)

            return Response({"message": "작성완료"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetailView(APIView):
    """EventDetailView
    GET:
    event_id를 사용하여, 해당 id의 행사정보를 조회합니다.
    읽기 권한은 제한하지 않아 읽기 위한 별도의 권한은 필요하지 않습니다.
    조회 성공 시, 해당 데이터를 출력하며, 200번 상태 메시지를 출력합니다.

    PUT:
    event_id를 사용하여 해당 행사정보를 수정합니다.
    permission을 주어, 행사정보의 작성자의 경우 해당 게시글을 수정할 수 있습니다.
    또한, superuser에게만 수정 권한을 부여합니다.
    partial을 이용하여 부분적인 수정이 가능합니다.
    event_id를 잘못입력하였을 때, 404 상태메시지를 출력합니다.
    성공적으로 수정 시 200 상태메시지를 출력합니다.
    수정하지 못했을 시 400 상태메시지를 출력합니다.

    DELETE:
    event_id를 사용허여 해당 행사정보를 삭제합니다.
    permission을 주어, 행사정보의 작성자의 경우 해당 게시글을 삭제할 수 있습니다.
    또한 superuser에게만 삭제 권한을 부여합니다.
    삭제에 성공하면, 200 상태메시지를 출력합니다.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CustomPermission]

    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        self.check_object_permissions(self.request, event)
        serializer = EventEditSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "수정완료"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        self.check_object_permissions(self.request, event)
        event.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_200_OK)
