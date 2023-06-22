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


class EventListView(generics.ListCreateAPIView):
    serializer_class = EventScrapSerializer
    queryset = EventList.objects.all()


class EventView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        CustomPermission,
    ]
    serializer_class = EventListSerializer
    queryset = Event.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "title",
    ]

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


class EventReviewView(generics.ListCreateAPIView):
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id, event_date):
        ticket = Ticket.objects.filter(event=event_id, event_date=str(event_date))
        serializer = TicketSerializer(ticket, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TicketTimeDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id, event_date, event_time):
        ticket = Ticket.objects.filter(
            event=event_id, event_date=str(event_date), event_time=str(event_time)
        )
        serializer = TicketSerializer(ticket, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeView(APIView):
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
            return Response("북마크가 취소되었습니다.", status=status.HTTP_200_OK)
        else:
            event.event_bookmarks.add(request.user)
            return Response("북마크 완료했습니다.", status=status.HTTP_200_OK)
