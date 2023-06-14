
from rest_framework.exceptions import NotFound
from rest_framework import status, permissions, generics
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from events.models import Event, EventReview, Ticket
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
    BookedTicketCountSerializer
)


# Create your views here.
class EventView(generics.ListCreateAPIView):
    """EventView
    GET:
    행사정보 전체를 볼 수 있습니다.
    generics를 사용하여, GET요청은  queryset사용하여, 따로 만들지 않았습니다.

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
    """EventDetailView
    GET:
    event_id를 사용하여, 해당 id의 행사정보를 조회합니다.
    읽기 권한은 제한하지 않아 읽기 위한 별도의 권한은 필요하지 않습니다.
    조회 성공 시, 해당 데이터를 출력하며, 200번 상태 메시지를 출력합니다.

    PUT:
    event_id를 사용하여 해당 행사정보를 수정합니다.
    permission을 주어, 행사정보의 작성자의 경우 해당 게시글을 수정할 수 있습니다.
    또한, admin에게만 수정 권한을 부여합니다.
    partial을 이용하여 부분적인 수정이 가능합니다.
    event_id를 잘못입력하였을 때, 404 상태메시지를 출력합니다.
    성공적으로 수정 시 200 상태메시지를 출력합니다.
    수정하지 못했을 시 400 상태메시지를 출력합니다.

    DELETE:
    event_id를 사용하여 해당 행사정보를 삭제합니다.
    permission을 주어, 행사정보의 작성자의 경우 해당 게시글을 삭제할 수 있습니다.
    또한 admin에게만 삭제 권한을 부여합니다.
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

class TicketView(generics.ListCreateAPIView):
    """
    [권한]
    permission_classes는 해당 클래스에서 사용할 permission을 결정합니다.
    IsAuthenticatedOrReadOnly는 로그인을 통해 인증한 회원인지 판별합니다. 아닌 경우 읽기 권한만 부여합니다.
    CustomPermission는 permissions.py에서 커스텀한 권한입니다
    [시리얼라이저]
    serializer_class는 해당 클래스에서 사용할 serializer을 결정합니다.
    [쿼리셋]
    queryset을 사용하여 어떻게 가져올지 결정합니다.
    Ticket모델의 모든 오브젝트를 가져와 get요청 시 보여줍니다.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CustomPermission]
    serializer_class = TicketCreateSerializer
    queryset = Ticket.objects.all()

    #이벤트_id를 가져와 시리얼라이저에 넣어줘 권한을 확인하기위해 get_serializer_context를 오버라이딩하여 사용했습니다.
    def get_serializer_context(self): 
        context = super(TicketView, self).get_serializer_context() 
        context.update({"event": self.kwargs["event_id"]}) 
        return context
    #위에 사용한 serializer_class를 가져와 serializer로 사용합니다. 시리얼라이저에 입력값을 넣고, 검증을 진행합니다   
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        event_id = self.kwargs.get("event_id")
        
        #try문에서는 event_id를 통해 해당 id를 가진 공연정보가 있는지 확인합니다.
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"message": "유효한 이벤트를 선택해 주세요"}, status=status.HTTP_400_BAD_REQUEST)            
        #통과 시 serializer_class에 요청한 데이터를 datada넣고, context(형식)에 event_id에는 해당 event_id, event에는 해당 event를 값으로 넣고 serializer로 보냅니다.
        serializer = self.get_serializer(data=request.data, context={"event_id": event_id, "event": event})
        
        #TicketCreateSerializer에서 모든 검증을 통과하면 
        #작성완료 메시지와 함께 상태메시지 201을 출력합니다, 통과하지 못한다면, 시리얼라이저에서 생성한 에러메시지와 상태메시지 400을 출력합니다.        
        if serializer.is_valid():
            serializer.save(author=request.user, event=event)
            return Response({"message": "작성완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TicketDetailView(APIView):
    """EventDetailView
    GET:
    ticket_id를 사용하여, 해당 id의 티켓을 조회합니다.
    읽기 권한은 제한하지 않아 읽기 위한 별도의 권한은 필요하지 않습니다.
    조회 성공 시, 해당 데이터를 출력하며, 200번 상태 메시지를 출력합니다.

    DELETE:
    ticket_id를 사용gk여 해당 티켓의 정보를 삭제합니다.
    permission을 주어, 티켓 작성자의 경우 해당 티켓을 삭제할 수 있습니다.
    또한 admin에게만 삭제 권한을 부여합니다.
    삭제에 성공하면, 200 상태메시지를 출력합니다.
    """

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
    

class BookingTicketView(APIView):
    """
    티켓_id를 사용하여, 해당 티켓을 조회, 예약, 예약 취소 기능을 합니다
    IsAuthenticated를 사용하여, 로그인한 회원만 사용가능합니다.
    """

    permission_classes = [permissions.IsAuthenticated]
    #get_object를 사용하여 해당하는 티켓의 정보를 조회합니다.
    def get(self, request, ticket_id):
            ticket = self.get_object(ticket_id)
            serializer = BookedTicketSerializer(ticket)
            return Response(serializer.data)
                                        
    def get_object(self, ticket_id):
        """
        ticket_id를 이용해서 티켓 정보를 가져옵니다.
        예약한 티켓이 없다면 예외처리를 통해 "예매한 티켓이 없습니다" 메시지와 상태메시지 404를 출력합니다.
        """
        try:
            return Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise NotFound(detail="예매한 티켓이 없습니다.", code=status.HTTP_404_NOT_FOUND)

    def post(self, request, ticket_id):
        """
        ticket_id를 이용해 티켓의 정보를 가져오는 get_object를 사용하여 티켓의 정보를 가져와 ticket에 넣습니다.
        serializer에 해당 ticket의 정보와 post요청을 보냅니다.
        
        요청을 보낸 회원이 이미 예매한 티켓이라면, 예매를 취소하고, current_booking의 값에 -1을 합니다
        보낸 요청이 잘 끝나면, "예매가 취소되었습니다." 메시지와 상태메시지 200을 출력합니다.
        
        요청을 보낸 회원이 예매하지 않은 티켓이라면, current_booking과 max_booking_count의 값을 비교합니다.
        current_booking의 값이 max_booking_count의 값보다 작다면
        예매가 진행되며, current_booking의 값에 +1을 하고 "예매가 완료되었습니다." 메시지와 상태메시지 200을 출력합니다.
        current_booking의 값이 max_booking_count의 값보다 크거나 같다면
        예매가 진행되지 않으며, "매진되었습니다." 메시지와 상태메시지 400을 출력합니다.
        """
        ticket = self.get_object(ticket_id)
        serializer = BookedTicketCountSerializer(ticket, data=request.data)
        
        if request.user in ticket.booked_users.all():
            ticket.booked_users.remove(request.user)
            serializer.instance.current_booking -= 1
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "예매가 취소되었습니다."}, status=status.HTTP_200_OK)
        else:
            if serializer.instance.current_booking >= serializer.instance.max_booking_count:
                    return Response({"message": "매진되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
            else:                  
                ticket.booked_users.add(request.user)
                serializer.instance.current_booking += 1
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"message": "예매가 완료되었습니다."}, status=status.HTTP_200_OK)    

class BookingTicketListView(generics.ListAPIView):
    """
    회원이 예약한 모든 티켓의 정보를 출력합니다.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookedTicketSerializer

    def get_queryset(self):
        user = self.request.user
        booked_tickets = user.booked_tickets.all()
        return booked_tickets
