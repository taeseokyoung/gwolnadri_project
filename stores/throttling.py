from rest_framework.throttling import UserRateThrottle


class ObjectThrottle(UserRateThrottle):
    rate = "1/s"
