from rest_framework import status, permissions
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from events.models import Event, EventReview
from events.permissons import CustomPermission, IsOwnerOrReadOnly
from events.serializers import (
    EventCreateSerializer,
    EventSerializer,
    EventListSerializer,
    EventEditSerializer,
    EventReviewSerializer,
    EventReviewCreateSerializer,
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


class EventReviewView(generics.ListCreateAPIView):
    """
    GET
    event_id를 사용하여 해당 id의 공연정보에 담긴 리뷰를 불러옵니다
    리뷰는 최신순으로 정렬하여 출력됩니다

    POST
    event_id를 사용하여 해당 id의 공연정보에 리뷰를 추가합니다
    인증은 context를 이용하며, 작성한 내용에 문제가 없을 시
    "작성완료"메시지와 상태메시지 200을 출력합니다
    입력값의 형태가 잘못되었을 시 상태메시지 400을 출력합니다.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = EventReviewSerializer
    queryset = None

    def get(self, request, *args, **kwargs):
        reviews = (
            get_object_or_404(Event, id=kwargs.get("event_id"))
            .review_set.all()
            .order_by("-created_at")
        )
        self.queryset = reviews
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = EventReviewCreateSerializer(
            data=request.data, context={"request": request}
        )
        event = get_object_or_404(Event, id=kwargs.get("event_id"))
        if serializer.is_valid():
            serializer.save(author=request.user, event=event)
            return Response({"message": "작성완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventReviewDetailView(APIView):
    """
    permission을 주어, 인증여부를 판단하며, IsOwnerOrReadOnly을 사용하여, 리뷰 생성자와 요청자를 확인합니다.
    PUT
    eventreview_id를 사용하여, 해당 id의 리뷰를 수정합니다
    수정이 잘 이루어지면, "수정완료"메시지와 상태메시지 200을 출력합니다
    입력값이 잘못되면, 상태메시지 400을 출력합니다
    DELETE
    eventreview_id를 사용하여 해당 id의 리뷰를 삭제합니다
    삭제가 잘 이루어지면, "삭제완료"메시지와 상태메시지 204를 출력합니다.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def put(self, request, **kwargs):
        review = get_object_or_404(EventReview, id=kwargs.get("eventreview_id"))
        serializer = EventReviewCreateSerializer(review, data=request.data)
        self.check_object_permissions(self.request, review)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "수정완료"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        review = get_object_or_404(EventReview, id=kwargs.get("eventreview_id"))
        self.check_object_permissions(self.request, review)
        review.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_204_NO_CONTENT)
