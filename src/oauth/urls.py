from django.urls import path
from .endpoint import views, auth_views
from .endpoint.auth_views import send_verification_email, verify_code

urlpatterns = [
    path('me/', views.UserView.as_view({'get': 'retrieve', 'put': 'update'})),

    path('author/', views.AuthorView.as_view({'get': 'list'})),

    path('author/<int:pk>', views.AuthorView.as_view({'get': 'retrieve'})),


    path('social/', views.SocialLinkView.as_view({'get': 'list', 'post': 'create'})),
    path('social/<int:pk>/', views.SocialLinkView.as_view({'put': 'update', 'delete': 'destroy'})),


    path('google/', auth_views.google_auth),
    path('spotify-callback/', auth_views.spotify_auth),

    path('spotify-login/', auth_views.spotify_login),
    path('', auth_views.google_login),

    path('send-email/', send_verification_email, name='send-verification-email'),
    path('verify-code/', verify_code, name='verify-code'),
]