from django.urls import path, include
from events import views

urlpatterns = [
    path("", views.EventView.as_view(), name="event_view"),
    path("<int:event_id>/", views.EventDetailView.as_view(), name="event_detail_view"),
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
        "<int:ticket_id>/bookedticket/",
        views.BookingTicketView.as_view(),
        name="booking_ticket_view",
    ),
    path(
        "bookedlist/",
        views.BookingTicketListView.as_view(),
        name="booked_list_view",
    ),
]
