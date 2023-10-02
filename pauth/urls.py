from rest_framework import routers

from pauth import views

router = routers.SimpleRouter()
router.register(r"", views.UserViewSet)

urlpatterns = router.urls
