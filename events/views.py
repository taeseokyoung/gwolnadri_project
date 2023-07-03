from rest_framework.exceptions import NotFound
from rest_framework import status, permissions, generics
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from events.models import Event, EventReview, Ticket, TicketBooking, EventList
from rest_framework import filters
from events.permissons import CustomPermission, IsOwnerOrReadOnly
from events.serializers import (
    EventCreateSerializer,
    EventSerializer,
    EventListSerializer,
    EventEditSerializer,
    EventReviewSerializer,
    EventReviewCreateSerializer,
    TicketCreateSerializer,
    TicketSerializer,
    BookedTicketSerializer,
    BookedTicketCountSerializer,
    EventScrapSerializer,
)


class EventListView(APIView):
    def get(self, request):
        eventlist = EventList.objects.all()
        serializer = EventScrapSerializer(eventlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CustomPermission]
    serializer_class = EventListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "title",
    ]

    def get(self, request):
        event = Event.objects.all().order_by("-created_at")
        serializer = EventListSerializer(event, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)

            return Response({"message": "작성완료"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetailView(APIView):
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


class EventReviewView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = EventReviewSerializer

    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        review = EventReview.objects.filter(event=event).order_by("-created_at")
        serializer = EventReviewSerializer(review, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

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


class TicketView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CustomPermission]
    serializer_class = TicketCreateSerializer

    # 이벤트_id를 사용하여 해당 이벤트에 생성된 티켓을 조회합니다.

    def get(self, request, event_id):
        tickets = Ticket.objects.filter(event=event_id)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super(TicketView, self).get_serializer_context()
        context.update({"event": self.kwargs["event_id"]})
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        event_id = self.kwargs.get("event_id")

        try:
            event = Event.objects.get(id=event_id)

        except Event.DoesNotExist:
            return Response(
                {"message": "유효한 이벤트를 선택해 주세요"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            data=request.data, context={"event_id": event_id, "event": event}
        )

        if serializer.is_valid():
            serializer.save(author=request.user, event=event)
            return Response({"message": "작성완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CustomPermission]

    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        self.check_object_permissions(self.request, ticket)
        ticket.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_200_OK)


class TicketDateDetailView(APIView):
    """
    공연id, 공연날짜를 이용하여, 해당 값에 맞는 티켓의 정보를 조회합니다.
    로그인한 회원만 사용가능합니다.
    event_date의 타입이 date 타입이기 때문에 url에서 사용하기 위해서 event_date의 타입은 str형으로 사용되어야 합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id, event_date):
        ticket = Ticket.objects.filter(event=event_id, event_date=str(event_date))
        serializer = TicketSerializer(ticket, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TicketTimeDetailView(APIView):
    """
    공연id, 공연날짜, 공연 시간을 이용하여, 해당 값에 맞는 티켓의 정보를 조회합니다.
    로그인한 회원만 사용가능합니다.
    event_date의 타입이 date 타입이기 때문에 url에서 사용하기 위해서 event_date의 타입은 str형으로 사용되어야 합니다.
    event_time의 타입이 varchar 타입이기 때문에 url에서 사용하기 위해서 event_time의 타입은 str형으로 사용되어야 합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id, event_date, event_time):
        ticket = Ticket.objects.filter(
            event=event_id, event_date=str(event_date), event_time=str(event_time)
        )
        serializer = TicketSerializer(ticket, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeView(APIView):
    """
    게시글 좋아요 기능을 수행합니다.
    로그인하여 검증된 회원만 사용이 가능합니다.
    POST
    post 요청 시 해당 event_id를 가진 공연정보의 likes 필드에 요청한 회원을 생성합니다.
    요청 성공 시 상태메시지 200을 출력합니다
    해당 likes 필드에 요청한 회원이 없을 경우 "like했습니다."메시지를 출력합니다
    해당 likes 필드에 요청한 회원이 있을 경우 "unlike했습니다.: 메시지를 출력합니다
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        if request.user in event.likes.all():
            event.likes.remove(request.user)
            return Response({"message": "unlike했습니다."}, status=status.HTTP_200_OK)
        else:
            event.likes.add(request.user)
            return Response({"message": "like했습니다."}, status=status.HTTP_200_OK)


class BookingTicketDetailView(APIView):
    """
    예매한 티켓을 조회하기 위해 사용됩니다.
    id는 예약항목의 id를 나타냅니다.
    조회하는 회원의 예약항목의 id를 사용하여, 해당 id를 가진 티켓의 정보를 조회합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            user = self.request.user
            ticket_booking = TicketBooking.objects.filter(id=id, author=user).first()
            if not ticket_booking:
                return Response(
                    {"message": "예매한 티켓이 없습니다."}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = BookedTicketSerializer(ticket_booking)
            return Response(serializer.data)
        except TicketBooking.DoesNotExist:
            return Response(
                {"message": "예매한 티켓이 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )


class BookingTicketView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ticket_id):
        """
        예매를 진행하기 위해 사용됩니다.
        ticket_id를 받아 해당 티켓이 존재하는지 먼저 확인합니다
        해당, 티켓이 존재하지 않는다면, "티켓이 존재하지 않습니다." 메시지와 404 상태메시지를 출력합니다

        시리얼라이저를 통해 입력값이 정확한 형태로 들어왔는지 확인합니다
        quantity의 값을 0 이하로 입력할 시 "올바른 수량(quantity)을 입력해주세요." 메시지와 400 상태메시지를 출력합니다
        current_booking(현재 예매된 티켓의 수량)의 값이 quantity(예매하고자 하는 수량)을 더하여 max_booking_count(최대 수량)을 넘을 경우
        "예매가 불가능합니다." 메시지와 400 상태메시지를 출력합니다

        예매가 가능한 상황이라면, current_booking에 quantity 값을 더해주고, 더해준 값을 해당 티켓에 저장해주고, 예매 내역을 ticket_booking에 저장해주고
        "예매가 완료되었습니다." 메시지와 201 상태메시지를 출력합니다.
        """

        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {"message": "티켓이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookedTicketCountSerializer(data=request.data)
        if serializer.is_valid():
            quantity = request.data.get("quantity", 0)
            if quantity is None or quantity <= 0:
                return Response(
                    {"message": "올바른 수량(quantity)을 입력해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if ticket.current_booking + quantity > ticket.max_booking_count:
                return Response(
                    {"message": "예매가 불가능합니다."}, status=status.HTTP_400_BAD_REQUEST
                )

            ticket_booking = TicketBooking(
                author=request.user,
                ticket=ticket,
                money=ticket.money,
                quantity=quantity,
            )
            ticket.current_booking += quantity
            ticket.save()
            ticket_booking.save()

            serializer = BookedTicketCountSerializer(ticket_booking)
            return Response({"message": "예매가 완료되었습니다."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingTicketListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookedTicketSerializer

    def get_queryset(self):
        user = self.request.user
        booked_tickets = TicketBooking.objects.filter(author=user)
        return booked_tickets


class EventBookmarkView(APIView):
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        if request.user in event.event_bookmarks.all():
            event.event_bookmarks.remove(request.user)
            return Response({"message": "북마크가 취소되었습니다."}, status=status.HTTP_200_OK)
        else:
            event.event_bookmarks.add(request.user)
            return Response({"message": "북마크 완료했습니다."}, status=status.HTTP_200_OK)
