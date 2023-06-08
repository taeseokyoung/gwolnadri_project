from rest_framework import permissions


class CustomPermission(permissions.BasePermission):
    """
    읽기 권한은 비로그인, 로그인 일반 회원 모두에게 주어집니다.
    생성, 수정, 삭제 권한은 오직 admin에게만 주어집니다.
    권한이 없을 경우 "권한이 없습니다" 메시지와 함께 상태메시지 403 에러를 발생시킵니다.
    """

    message = "권한이 없습니다"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_admin
