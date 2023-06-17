from django.urls import path, include
from events import views

urlpatterns = [
    path("", views.EventView.as_view(), name="event_view"),
    path("<int:event_id>/", views.EventDetailView.as_view(), name="event_detail_view"),
    path("<int:event_id>/like/", views.LikeView.as_view(), name="like"),
    path(
        "<int:event_id>/review/",
        views.EventReviewView.as_view(),
        name="event_review_view",
    ),
    path(
        "<int:event_id>/<int:eventreview_id>",
        views.EventReviewDetailView.as_view(),
        name="event_review_detail_view",
    ),
    path("<int:event_id>/booking/", views.TicketView.as_view(), name="ticket_view"),
    path(
        "<int:ticket_id>/ticket/",
        views.TicketDetailView.as_view(),
        name="ticket_detail_view",
    ),
    path(
        "<int:event_id>/<str:event_date>/ticket/",
        views.TicketDateDetailView.as_view(),
        name="ticket_date_detail_view",
    ),
    path(
        "<int:event_id>/<str:event_date>/<str:event_time>/ticket/",
        views.TicketTimeDetailView.as_view(),
        name="ticket_time_detail_view",
    ),
    path(
        "<int:ticket_id>/bookedticket/",
        views.BookingTicketView.as_view(),
        name="booking_ticket_view",
    ),
    path(
        "<int:id>/bookedtickets/", views.BookingTicketDetailView.as_view(), name="booking_ticket_detail_view",
    ),
    path(
        "bookedlist/",
        views.BookingTicketListView.as_view(),
        name="booked_list_view",
    ),
    path(
        "<int:event_id>/bookmark/",
        views.EventBookmarkView.as_view(),
        name="bookmark_event_view",
    ),
]
