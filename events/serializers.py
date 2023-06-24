from rest_framework import serializers
from events.models import Event, EventReview, Ticket, TicketBooking, EventList
from users.models import User
from datetime import datetime


class EventScrapSerializer(serializers.ModelSerializer):
   """
   크롤링한 공연정보를 보여주는 시리얼라이저입니다.
   """
    class Meta:
        model = EventList
        fields = "__all__"

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
    created_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    event_start_date = serializers.DateTimeField(format="%y.%m.%d", read_only=True)
    event_end_date = serializers.DateTimeField(format="%y.%m.%d", read_only=True)
    review_count = serializers.SerializerMethodField()

    likes_count = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        author = obj.author.email.split("@")[0]
        return author

    def get_review_count(self, obj):
        return obj.review_set.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
        model = Event
        fields = (
            "id",
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
    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "image",
            "event_start_date",
            "event_end_date",
            "review_count",
            "likes_count",
            "event_bookmarks",
        )


class EventEditSerializer(serializers.ModelSerializer):
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
    created_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    author_name = serializers.SerializerMethodField()

    def get_author_name(self, obj):
        # author_name = obj.author.username
        return obj.author.username

    class Meta:
        model = EventReview
        fields = (
            "id",
            "author",
            "author_name",
            "event",
            "content",
            "review_image",
            "created_at",
            "updated_at",
            "grade",
        )


class EventReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReview
        fields = (
            "content",
            "grade",
            "review_image",
        )


class TicketCreateSerializer(serializers.ModelSerializer):
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
