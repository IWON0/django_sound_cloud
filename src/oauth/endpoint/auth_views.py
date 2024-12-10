from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from .. import serializer
from ..services import google, spotify


def google_login(request):
    """Страница входа через Google"""
    return render(request, 'oauth/google_login.html')


def spotify_login(request):
    """Страница входа через Spotify"""
    return render(request, 'oauth/spotify_login.html')


@api_view(["POST", "OPTIONS"])
def google_auth(request):
    if request.method == "OPTIONS":
        # Обработка preflight-запроса
        return Response(headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        })

    # Ваш текущий код для обработки POST-запросов:
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