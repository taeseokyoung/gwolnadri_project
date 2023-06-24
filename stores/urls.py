from django.urls import path
from stores import views

urlpatterns = [
    path("", views.StoreListView.as_view(), name="store_list"),
    path("<int:store_id>/", views.StoreDetailView.as_view(), name="store_detail_view"),
    path("<int:store_id>/comments/", views.CommentView.as_view(), name="comment_view"),
    path(
        "<int:store_id>/comments/<int:comment_id>/",
        views.CommentDetailView.as_view(),
        name="comment_detail_view",
    ),
    path("<int:store_id>/like/", views.LikeView.as_view(), name="like_view"),
    path(
        "hanbok/<int:hanbok_id>/",
        views.HanbokDetailView.as_view(),
        name="hanbok_detail",
    ),
    path(
        "payment/<int:user_id>/",
        views.PurchaseRecordView.as_view(),
        name="purchase_record",
    ),
    path(
        "payment/<int:user_id>/hanbok/",
        views.HanbokPurchaseRecordView.as_view(),
        name="hanbok_purchase_record",
    ),
    path(
        "payment/<int:user_id>/event/",
        views.EventPurchaseRecordView.as_view(),
        name="event_purchase_record",
    ),
    path(
        "payment/<tid>/",
        views.PutPurchaseRecordView.as_view(),
        name="put_purchase_record",
    ),
    path(
        "payment/<int:user_id>/<tid>/",
        views.GetPurchaseRecordView.as_view(),
        name="get_purchase_record",
    ),
    path(
        "<int:store_id>/bookmark/",
        views.StoreBookmarkView.as_view(),
        name="bookmark_store_view",
    ),
    path(
        "payment/<int:user_id>/hanbok/",
        views.HanbokPurchaseRecordView.as_view(),
        name="hanbok_purchase_record",
    ),
    path(
        "payment/<int:user_id>/event/",
        views.EventPurchaseRecordView.as_view(),
        name="event_purchase_record",
    ),
]
