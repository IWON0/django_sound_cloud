from datetime import datetime
from typing import Optional

import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

from src.oauth.models import AuthUser


class AuthBackend(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request) -> Optional[tuple]:
        # Получаем заголовок Authorization
        auth_header = authentication.get_authorization_header(request)

        # Проверяем, что заголовок есть
        if not auth_header:
            return None

        # Разбиваем заголовок на части
        try:
            auth_header_parts = auth_header.split()
        except ValueError:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")

        # Проверяем, что заголовок состоит из 2 частей: "Token <token>"
        if len(auth_header_parts) != 2 or auth_header_parts[0].lower() != self.authentication_header_prefix.lower().encode():
            return None

        # Декодируем токен
        try:
            token = auth_header_parts[1].decode('utf-8')
        except UnicodeError:
            raise exceptions.AuthenticationFailed("Token contains invalid characters.")

        # Передаем токен на дальнейшую обработку
        return self.authenticate_credential(token)

    def authenticate_credential(self, token) -> tuple:
        # Декодируем токен
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired.")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token.")

        # Проверяем, что пользователь существует
        try:
            user = AuthUser.objects.get(id=payload['user_id'])
        except AuthUser.DoesNotExist:
            raise exceptions.AuthenticationFailed("No user matching this token was found.")

        # Возвращаем пользователя
        return user, None
