import json
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, token_blacklist
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.http import HttpResponse

def checkhealth(request):
    return HttpResponse(json.dumps("Backend is Up."), content_type="application/json")

urlpatterns = [
    path("checkhealth/", checkhealth, name="checkhealth"),
    path("api/", include("core.urls")),         # your app’s API routes
    
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]
