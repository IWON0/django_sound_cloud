from rest_framework import generics, viewsets

from . import models, serializer
from ..base.permissions import IsAuthor


class GenreView(generics.ListAPIView):
    """List of genres"""
    queryset = models.Genre.objects.all()
    serializer_class = serializer.GenreSerializer


class LicenseView(viewsets.ModelViewSet):
    """CRUD author licenses"""
    serializer_class = serializer.LicenseSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.License.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)