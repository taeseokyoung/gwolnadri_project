from rest_framework import serializers
from events.models import Event, EventReview, Ticket, TicketBooking
from users.models import User
from datetime import datetime


class EventCreateSerializer(serializers.ModelSerializer):
    """
    공연정보를 작성하기 위해 사용합니다.
    title (varchar),
    content (text),
    image (image),
    event_start_date (date),
    event_end_date (date),
    time_slots (JSON),
    max_booking (Positiveint),
    money (int),
    값이 필요합니다.
    """

    class Meta:
        model = Event
        fields = (
            "title",
            "content",
            "image",
            "event_start_date",
            "event_end_date",
            "time_slots",
            "max_booking",
            "money",
        )


class EventSerializer(serializers.ModelSerializer):
    """
    게시글의 모든 정보를 보여주기 위해 사용됩니다.

    format을 사용하여 created_at의 출력형태를 제어합니다.
    review_count는 해당 행사정보에 담긴 리뷰의 수를 나타냅니다.
    likes_count는 해당 행사정보의 좋아요 수를 나타냅니다.
    """

    created_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    event_start_date = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    event_end_date = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    review_count = serializers.SerializerMethodField()

    likes_count = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        author = obj.author.email.split("@")[0]
        return author

    def get_review_count(self, obj):
        return obj.review_set.count()

    likes_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
        model = Event
        fields = (
            "author",
            "title",
            "content",
            "image",
            "created_at",
            "updated_at",
            "event_start_date",
            "event_end_date",
            "time_slots",
            "max_booking",
            "money",
            "likes",
            "review_count",
            "likes_count",
            "event_bookmarks",
        )


class EventListSerializer(EventSerializer):
    """EventListSerializer: Event의 간단한 정보

    Event의 일부 정보만 조회하여 목록을 형성할 때 사용합니다.
    review_count는 해당 행사정보에 담긴 리뷰의 수를 나타냅니다.
    likes_count는 해당 행사정보의 좋아요 수를 나타냅니다.
    """

    class Meta:
        """
        id는 Event_id 입니다.
        """

        model = Event
        fields = (
            "title",
            "event_start_date",
            "event_end_date",
            "review_count",
            "likes_count",
            "event_bookmarks",
        )


class EventEditSerializer(serializers.ModelSerializer):
    """Event정보를 수정할 때 사용

    Raises:
        검증 시 event_start_date와 event_end_date가 있어야 하며,
        event_start_date가 event_end_date보다 작을 경우 에러발생

    Returns:
        수정된 정보를 출력
    """

    class Meta:
        model = Event
        fields = "__all__"

    def validate(self, attrs):
        event_start_date = attrs.get("event_start_date")
        event_end_date = attrs.get("event_end_date")
        if event_start_date and event_end_date and event_end_date <= event_start_date:
            raise serializers.ValidationError(
                "event_end_date must be greater than event_start_date"
            )

        return attrs


class EventReviewSerializer(serializers.ModelSerializer):
    """
    리뷰를 조회하기 위해 사용됩니다.
    """

    created_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)

    class Meta:
        model = EventReview
        fields = "__all__"


class EventReviewCreateSerializer(serializers.ModelSerializer):
    """
    리뷰를 생성하기 위해 사용됩니다.
    content(text)
    grade(intchoice)
    """

    class Meta:
        model = EventReview
        fields = (
            "content",
            "grade",
        )


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    티켓을 생성하기 위해 사용합니다.
    event_date(Date)
    event_time(Char)
    max_booking_count(int)
    값을 입력 받습니다.

    validate
    event_id를 사용하여 해당 공연이 있는지 확인합니다
    없을 시 "유효한 이벤트를 선택해 주세요" 메시지를 출력합니다

    event_date
    event_start_date~event_end_date 사이의 값이 입력되었는지 확인합니다.
    YYYY-MM-DD 형태로 입력합니다.

    event_time
    time_slots의 value를 탐색하여 입력된 event_time의 값이 있는지 확인합니다
    없을 시 "공연 시간을 확인해 주세요" 메시지를 출력합니다

    max_booking_count
    Event 모델의 max_bookig의 값과 비교하여 같은지 확인합니다.
    다를 시 "최대 관객수를 확인해 주세요" 메시지를 출력합니다
    """

    event_date = serializers.DateField()
    event_time = serializers.CharField(max_length=11)
    booked_users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    current_booking = serializers.IntegerField(read_only=True)

    def validate(self, attrs):
        event_id = self.context.get("event_id")
        event_date = attrs.get("event_date")
        event_time = attrs.get("event_time")
        max_booking_count = attrs.get("max_booking_count")

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError("유효한 이벤트를 선택해 주세요")

        if (
            event.event_start_date.date() > event_date
            and event_date < event.event_end_date.date()
        ):
            raise serializers.ValidationError("공연 기간을 확인해 주세요")

        time_slots = event.time_slots

        if event_time not in time_slots.values():
            raise serializers.ValidationError("공연 시간을 확인해 주세요")

        max_bookig = event.max_booking
        if max_booking_count != max_bookig:
            raise serializers.ValidationError("최대 관객수를 확인해 주세요")

        attrs["event"] = event
        return attrs

    class Meta:
        model = Ticket
        fields = "__all__"
        read_only_fields = ("author", "event")


class TicketSerializer(serializers.ModelSerializer):
    """
    생성한 티켓의 정보를 확인할 때 사용되는 시리얼라이저 입니다.
    """

    class Meta:
        model = Ticket
        fields = "__all__"


class BookedTicketSerializer(serializers.ModelSerializer):
    """
    예약한 티켓을 조회하기 위해 사용됩니다.
    """

    event = serializers.SerializerMethodField()
    event_date = serializers.SerializerMethodField()
    event_time = serializers.SerializerMethodField()
    quantity = serializers.IntegerField(min_value=1)

    def get_event(self, ticket_booking):
        return ticket_booking.ticket.event.title

    def get_event_date(self, ticket_booking):
        return ticket_booking.ticket.event_date.strftime("%m월%d일 %H:%M")

    def get_event_time(self, ticket_booking):
        return ticket_booking.ticket.event_time

    class Meta:
        model = TicketBooking
        fields = (
            "event",
            "event_date",
            "event_time",
            "quantity",
            "money",
        )


class BookedTicketCountSerializer(serializers.ModelSerializer):
    """
    티켓 예약을 위해 만들어진 시리얼라이저 입니다
    current_booking과 max_booking_count을 이용하여, 티켓의 예약 가능여부를 판단합니다
    """

    author = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    current_booking = serializers.IntegerField(read_only=True)
    max_booking_count = serializers.IntegerField(read_only=True)
    money = serializers.SerializerMethodField(read_only=True)
    quantity = serializers.SerializerMethodField()

    def get_current_booking(self, ticket):
        return ticket.current_booking

    def get_max_booking_count(self, ticket):
        return ticket.max_booking_count

    def get_author(self, ticket_booking):
        return ticket_booking.author.username

    def get_event(self, ticket_booking):
        return ticket_booking.ticket.event.title

    def get_money(self, ticket_booking):
        return ticket_booking.ticket.money

    def get_quantity(self, ticket_booking):
        return ticket_booking.quantity

    class Meta:
        model = TicketBooking
        fields = (
            "author",
            "event",
            "money",
            "quantity",
            "current_booking",
            "max_booking_count",
        )


# 북마크용 Serializer
class EventBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "title",
            "content",
            "image",
            "created_at",
            "updated_at",
            "event_start_date",
            "event_end_date",
            "likes",
            "likes_count",
        )
