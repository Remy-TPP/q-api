from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.recommendations.views import RecommendationViewSet, Recommendation2ViewSet


router = SimpleRouter()

# TODO: remove
router.register(r'', RecommendationViewSet, 'recommendations')
# TODO: would be better to move to something like '/recipes/recommend_me'
router.register(r'', Recommendation2ViewSet, 'recommendations2')


urlpatterns = [
    path('', include(router.urls)),
]
