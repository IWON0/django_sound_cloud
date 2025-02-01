from django.contrib import admin
from django.urls import path, include

from src.oauth.endpoint.auth_views import verify_code, send_verification_email

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('src.oauth.urls')),
    path('api/v1/', include('src.routes')),
    path('api/v1/auth/send-verification-email/', send_verification_email, name='send-verification-email'),
    path('api/v1/auth/verify-code/', verify_code, name='verify-code'),
]
