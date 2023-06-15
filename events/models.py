from django.db import models
from users.models import User
from django.core.validators import MinValueValidator

"""Event 모델

공연 정보를 담습니다.

Attributes:
author (Foreignkey): user_id의 값을 가집니다
title (varchar): 공연 제목, 50자 제한
content (text): 공연 내용
image (image): 공연에 관한 이미지
created_at (date): 생성일자 
updated_at (date): 수정일자
event_start_date (date): 공연 시작일 
event_end_date (date): 공연 종료일 
time_slots (JSON): 공연 시간 정보를 JSON형태로 담습니다.
max_booking (Positiveint): 최대 관객수를 담습니다.
MinValueValidator(1): 1 이상의 값만 입력가능
money (int): 공연 입장료   
likes (ManyToMany): 유저 테이블과 다 대 다 관계를 통해 좋아요 기능
"""


class Event(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    image = models.ImageField(blank=True, upload_to="%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_start_date = models.DateTimeField()
    event_end_date = models.DateTimeField()
    time_slots = models.JSONField()
    max_booking = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    money = models.IntegerField()
    likes = models.ManyToManyField(User, related_name="like_event", blank=True)
    event_bookmarks = models.ManyToManyField(
        User, related_name="bookmark_events", blank=True
    )


class Ticket(models.Model):
    """
    author(ForeingnKey): user_id 값을 가집니다.(티켓생성자)
    event(ForeingnKey): event_id 값을 가집니다. (티켓을 사용하는 공연)
    event_date(Date): 해당 공연의 날짜의 값을 가집니다. (해당 티켓을 사용할 수 있는 공연의 날짜)
                      11자로 표현해야 하며, HH:MM~HH:MM 으로 표현하면 됩니다(H:시간, M:분)
    event_time(Char): 해당 공연의 시간 값을 가집니다. (해당 티켓을 사용할 수 있는 공연의 시간)
    booked_user(ManyToMany): 해당 티켓을 예매한 유저를 저장합니다.
    max_booking_count(PositiveInteger): 최대 관객 수를 표현합니다. 최소 1 이상의 int형 값을 넣어야 합니다.
    current_booking(PositiveInteger): 현재 예매한 인원의 수를 표현합니다.
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_date = models.DateField()
    event_time = models.CharField(max_length=11)
    booked_users = models.ManyToManyField(User, related_name="booked_tickets")
    max_booking_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    current_booking = models.PositiveIntegerField(default=0)


class EventReview(models.Model):
    """
    해당 공연정보에 담긴 리뷰를 보여줍니다.
    author(Foreignkey) 해당 리뷰를 작성한 작성자
    event(Foreignkey) 해당 리뷰의 대상이 된 행사정보
    content(text) 리뷰의 내용
    review_image(image) 리뷰에 입력된 이미지
    created_at(date) 생성날짜
    updated_at(date) 수정시간
    grade(int choice) 해당 행사의 평점을 나타내며, 1~5점을 줄 수 있습니다.
    """

    RATING_CHOICES = [
        (1, "1점"),
        (2, "2점"),
        (3, "3점"),
        (4, "4점"),
        (5, "5점"),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="review_set"
    )
    content = models.TextField()
    review_image = models.ImageField(blank=True, upload_to="%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    grade = models.IntegerField(choices=RATING_CHOICES)
