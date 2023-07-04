from django.db import models
from taggit.managers import TaggableManager
from users.models import User
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)


class Event(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    image = models.ImageField(blank=True, upload_to="%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_start_date = models.DateTimeField(null=True)
    event_end_date = models.DateTimeField(null=True)
    time_slots = models.JSONField(null=True)
    max_booking = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=True
    )
    money = models.IntegerField(null=True)
    likes = models.ManyToManyField(User, related_name="like_event", blank=True)
    event_bookmarks = models.ManyToManyField(
        User, related_name="bookmark_events", blank=True
    )
    tags = TaggableManager(blank=True)
    event_category = models.ForeignKey(Category, on_delete=models.CASCADE)


class EventList(models.Model):
    title = models.CharField(max_length=50)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    image = models.CharField(max_length=500, null=True)


class Ticket(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_date = models.DateField()
    event_time = models.CharField(max_length=11)
    max_booking_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    current_booking = models.PositiveIntegerField(default=0)
    money = models.IntegerField()
    quantity = models.IntegerField(default=0)


class TicketBooking(models.Model):
    """
    author(ForeignKey): 예약을 한 회원을 표현합니다.
    ticket(ForeignKey): 예약 대상이 된 티켓의 id를 표현합니다
    money(int): 티켓의 가격을 표현합니다.
    quantity(int): 구입할 수량을 표현합니다
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    money = models.IntegerField()
    quantity = models.IntegerField(default=0)


class EventReview(models.Model):
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
    content = models.TextField(max_length=50)
    review_image = models.ImageField(blank=True, upload_to="%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    grade = models.IntegerField(choices=RATING_CHOICES)
