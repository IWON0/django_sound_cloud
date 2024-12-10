from rest_framework import viewsets, parsers, permissions

from .. import serializer, models


class UserView(viewsets.ModelViewSet):
    """Viewing and editing user data"""
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializer.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user

    def get_object(self):
        return self.get_queryset()


class AuthorView(viewsets.ReadOnlyModelViewSet):
    """list of authors"""
    queryset = models.AuthUser.objects.all()
    serializer_class = serializer.AuthorSerializer
