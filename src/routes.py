from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_spectacular.extensions import OpenApiAuthenticationExtension

#
# schema_view = get_schema_view(
#     openapi.Info(
#         title="Audio library",
#         default_version='v1',
#         description="Пример аудио библиотеки на Django Rest Framework",
#         contact=openapi.Contact(url="https://www.youtube.com/c/DjangoSchool"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

class CustomAuthExtension(OpenApiAuthenticationExtension):
    target_class = 'src.oauth.services.auth_backend.AuthBackend'
    name = 'CustomAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Введите токен в формате "Token <токен>"'  # Указываем формат "Token <token>"
        }


urlpatterns = [
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # # path('api/v1/', include('src.routes')),  # Переместите сюда
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('auth/', include('src.oauth.urls')),
    path('audio/', include('src.audio_library.urls')),
]
