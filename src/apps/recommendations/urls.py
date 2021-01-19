from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.recommendations.views import RecommendationViewSet


router = SimpleRouter()

router.register(r'', RecommendationViewSet, 'recommendations')


urlpatterns = [
    path('', include(router.urls)),
]
