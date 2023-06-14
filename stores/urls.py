from django.urls import path
from stores import views


urlpatterns = [
    path("", views.StoreListView.as_view(), name="store_list"),
    path("<int:store_id>/", views.StoreDetailView.as_view(), name="store_detail_view"),
    path("<int:store_id>/comments/", views.CommentView.as_view(), name="comment_view"),
    path(
        "payment/<int:user_id>/",
        views.PurchaseRecordView.as_view(),
        name="purchase_record",
    ),
    path(
        "payment/<tid>/",
        views.PutPurchaseRecordView.as_view(),
        name="put_purchase_record",
    ),
]
