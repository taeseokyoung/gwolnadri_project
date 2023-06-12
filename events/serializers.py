from rest_framework import serializers
from events.models import Event, EventReview


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
    """

    created_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    event_start_date = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    event_end_date = serializers.DateTimeField(format="%m월%d일 %H:%M", read_only=True)
    review_count = serializers.SerializerMethodField()

    def get_review_count(self, obj):
        return obj.review_set.count()

    class Meta:
        model = Event
        fields = "__all__"


class EventListSerializer(EventSerializer):
    """EventListSerializer: Event의 간단한 정보

    Event의 일부 정보만 조회하여 목록을 형성할 때 사용합니다.
    review_count는 해당 행사정보에 담긴 리뷰의 수를 나타냅니다.
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
