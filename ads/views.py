from rest_framework.viewsets import GenericViewSet

from ads.exceptions import ads_api_exception_handler


class BaseView(GenericViewSet):
    def get_exception_handler(self):
        return ads_api_exception_handler
