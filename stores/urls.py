from django.urls import path
from stores import views


urlpatterns = [
    path("", views.StoreListView.as_view(), name="store_list"),
    path("<int:store_id>/", views.StoreDetailView.as_view(), name="store_detail_view"),
]
