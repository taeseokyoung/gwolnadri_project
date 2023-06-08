from django.urls import path, include
from events import views

urlpatterns = [
    path("", views.EventView.as_view(), name="event_view"),
    path("<int:event_id>", views.EventDetailView.as_view(), name="event_detail_view"),
    path(
        "<int:event_id>/review/",
        views.EventReviewView.as_view(),
        name="event_review_view",
    ),
]
