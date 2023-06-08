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
