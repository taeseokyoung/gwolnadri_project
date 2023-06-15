from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Store, Hanbok, HanbokComment, PurchaseRecord
from .serializers import (
    StoreListSerializer,
    CreateStoreSerializer,
    HanbokSerializer,
    CreateHanbokSerializer,
    PurchaseRecordCreateSerializer,
    CommentSerializer,
    CreateCommentSerializer,
)


# 한복집 리스트
class StoreListView(APIView):
    """
    모든 한복집 리스트 -> 궁별 한복집 리스트로 변경할 예정
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        store = Store.objects.all()
        store_serializer = StoreListSerializer(store, many=True)

        return Response(
            {
                "StoreList": store_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if request.user.is_staff == True:
            serializer = CreateStoreSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=request.user)
                return Response(
                    {"message": "한복집추가완료", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"${serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "권한이 없거나 잘못된 요청입니다."}, status=status.HTTP_403_FORBIDDEN
            )


# 한복집 상세 페이지
class StoreDetailView(APIView):
    """
    해당 한복집의 정보와 등록한 한복 상품 정보, 리뷰 노출
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, store_id):
        store = get_object_or_404(Store, id=store_id)
        hanboks = Hanbok.objects.filter(store=store_id)
        comments = HanbokComment.objects.filter(store=store_id)

        store_serializer = StoreListSerializer(store)
        hanbok_serializer = HanbokSerializer(hanboks, many=True)
        comment_serializer = CommentSerializer(comments, many=True)

        return Response(
            {
                "Store": store_serializer.data,
                "HanbokList": hanbok_serializer.data,
                "Comment": comment_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, store_id):
        """
        staff인지 && 내가게인지 확인
        """
        my_store = list(Store.objects.filter(owner=request.user))
        this_store = list(Store.objects.filter(id=store_id))

        if (request.user.is_staff == True) and (
            (this_store == my_store) or (this_store[0] in my_store)
        ):
            serializer = CreateHanbokSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=request.user, store_id=store_id)
                return Response(
                    {"message": "한복 추가 완료", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"${serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "권한이 없거나 잘못된 요청입니다."}, status=status.HTTP_403_FORBIDDEN
            )

          
class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, store_id):
        """
        한복점에 달린 모든 리뷰만 열람
        """
        store = get_object_or_404(Store, id=store_id)
        comments = store.comments.all()
        comment_serializer = CommentSerializer(comments, many=True)
        return Response(
            {
                "Comment": comment_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, store_id):
        """
        한복점 리뷰 작성 로그인한 사람이면 모두 가능
        """
        comment_serializer = CreateCommentSerializer(data=request.data)
        if comment_serializer.is_valid():
            comment_serializer.save(store_id=store_id, user=request.user)
            return Response(
                {"message": "후기 추가 완료", "data": comment_serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": f"${comment_serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def put(self, request, store_id, comment_id):
        """
        한복점 리뷰 수정
        """
        comment = get_object_or_404(HanbokComment, id=comment_id, store_id=store_id)
        print("여기여기여기 : ", comment)
        if request.user == comment.user:
            serializer = CreateCommentSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save(store_id=store_id, id=comment_id)
                return Response(
                    {"message": "후기 수정 완료", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"${serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "권한이 없거나 잘못된 접근입니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def delete(self, request, store_id, comment_id):
        """
        한복점 리뷰 삭제
        """
        comment = get_object_or_404(HanbokComment, id=comment_id, store_id=store_id)
        if request.user == comment.user:
            comment.delete()
            return Response(
                {"message": "후기가 삭제되었습니다."},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"message": "권한이 없거나 잘못된 접근입니다."},
                status=status.HTTP_403_FORBIDDEN,
            )


class LikeView(APIView):
    def post(self, request, store_id):
        store = get_object_or_404(Store, id=store_id)
        if request.user in store.likes.all():
            store.likes.remove(request.user)
            return Response(
                {"message": "좋아요가 취소되었습니다"},
                status=status.HTTP_200_OK,
            )
        else:
            store.likes.add(request.user)
            return Response(
                {"message": "좋아요 눌렀습니다"},
                status=status.HTTP_200_OK,
            )

# 한복 상세페이지
class HanbokDetailView(APIView):
    def get(self, request, hanbok_id):
        hanbok = get_object_or_404(Hanbok, id=hanbok_id)
        serializer = HanbokSerializer(hanbok)
        return Response(serializer.data, status=status.HTTP_200_OK)



# 결제 승인요청
class PurchaseRecordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        decomplete = PurchaseRecord.objects.filter(
            user_id=user_id, approved_at__isnull=True
        )
        if decomplete.exists():
            decomplete.delete()
        serializer = PurchaseRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "db 저장완료"}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 결제 완료
class PutPurchaseRecordView(APIView):
    def get(self, request, tid):
        purchase_record = get_object_or_404(PurchaseRecord, tid=tid)
        serializer = PurchaseRecordCreateSerializer(purchase_record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, tid):
        purchase_record = get_object_or_404(PurchaseRecord, tid=tid)
        serializer = PurchaseRecordCreateSerializer(
            purchase_record, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "결제완료"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 한복점 북마크
class StoreBookmarkView(APIView):
    def post(self, request, store_id):
        store = get_object_or_404(Store, id=store_id)
        if request.user in store.store_bookmarks.all():
            store.store_bookmarks.remove(request.user)
            return Response("북마크가 취소되었습니다.", status=status.HTTP_200_OK)
        else:
            store.store_bookmarks.add(request.user)
            return Response("북마크 완료했습니다.", status=status.HTTP_200_OK)
