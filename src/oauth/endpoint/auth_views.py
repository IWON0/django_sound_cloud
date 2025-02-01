import random
from django.core.mail import send_mail
from django.conf import settings
import jwt
from datetime import timedelta, datetime

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from .. import serializer
from ..models import AuthUser
from ..services import google, spotify

verification_codes = {}


def google_login(request):
    """Страница входа через Google"""
    return render(request, 'oauth/google_login.html')


def spotify_login(request):
    """Страница входа через Spotify"""
    return render(request, 'oauth/spotify_login.html')


@api_view(["POST", "OPTIONS"])
def google_auth(request):
    if request.method == "OPTIONS":
        return Response(headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        })

    google_data = serializer.GoogleAuth(data=request.data)
    if google_data.is_valid():
        token = google.check_google_auth(google_data.data)
        return Response(token)
    else:
        return AuthenticationFailed(code=403, detail='Bad data Google')


@api_view(['GET'])
def spotify_auth(request):
    """Подтверждение атворизации через Spotify"""
    token = spotify.spotify_auth(request.query_params.get('code'))
    return Response(token)


@api_view(['POST'])
def send_verification_email(request):
    email = request.data.get('email')
    if not email:
        return Response({'message': 'Email обязателен'}, status=400)

    code = str(random.randint(100000, 999999))
    verification_codes[email] = code

    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {code}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    return Response({'message': 'Код отправлен на почту!'})


@api_view(['POST'])
def verify_code(request):
    email = request.data.get('email')
    code = request.data.get('code')

    if not email or not code:
        return Response({'message': 'Email и код обязательны'}, status=400)

    if verification_codes.get(email) != code:
        return Response({'message': 'Неверный код'}, status=400)

    user, created = AuthUser.objects.get_or_create(email=email)

    if not hasattr(user, 'is_email_verified'):
        return Response({'message': 'Ошибка сервера: поле is_email_verified отсутствует'}, status=500)

    if not user.is_email_verified:
        user.is_email_verified = True
        user.save()

    del verification_codes[email]

    token_data = {
        'user_id': user.id,
        'is_email_verified': user.is_email_verified,
    }
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    print(token)
    return Response({'access_token': token, 'token_type': 'Token'})
