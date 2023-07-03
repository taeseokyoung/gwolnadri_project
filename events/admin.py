from django.contrib import admin
from events.models import Event, EventReview, Ticket

admin.site.register(Event)
admin.site.register(EventReview)
admin.site.register(Ticket)
