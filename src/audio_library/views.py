import os

from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, parsers, views

from . import models, serializer
from ..base.classes import MixedSerializer, Pagination
from ..base.permissions import IsAuthor
from ..base.services import delete_old_file


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


class AlbumView(viewsets.ModelViewSet):
    """CRUD albums by the author"""
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializer.AlbumSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.Album.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()


class PublicAlbumView(generics.ListAPIView):
    """list of author's public albums"""
    serializer_class = serializer.AlbumSerializer

    def get_queryset(self):
        return models.Album.objects.filter(user__id=self.kwargs.get('pk'), private=False)


class TrackView(MixedSerializer, viewsets.ModelViewSet):
    """CRUD tracks"""
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [IsAuthor]
    serializer_class = serializer.CreateAuthorTrackSerializer
    serializer_classes_by_action = {
        'list': serializer.AuthorTrackSerializer
    }

    def get_queryset(self):
        return models.Track.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        delete_old_file(instance.file.path)
        instance.delete()


class PlayListView(MixedSerializer, viewsets.ModelViewSet):
    """CRUD of user playlists"""
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [IsAuthor]
    serializer_class = serializer.CreatePlayListSerializer
    serializer_classes_by_action = {
        'list': serializer.PlayListSerializer
    }

    def get_queryset(self):
        return models.PlayList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()


class TrackListView(generics.ListAPIView):
    """list of all tracks"""
    queryset = models.Track.objects.filter(album__private=False, private=False)
    serializer_class = serializer.AuthorTrackSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'user__display_name', 'album__name', 'genre__name']


class AuthorTrackListView(generics.ListAPIView):
    """list of all tracks by the author"""
    serializer_class = serializer.AuthorTrackSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'album__name', 'genre__name']

    def get_queryset(self):
        return models.Track.objects.filter(
            user__id=self.kwargs.get('pk'), album__private=False, private=False
        )


class CommentAuthorView(viewsets.ModelViewSet):
    """CRUD author's comments"""
    serializer_class = serializer.CommentAuthorSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.Comment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentView(viewsets.ModelViewSet):
    """track comments"""
    serializer_class = serializer.CommentSerializer

    def get_queryset(self):
        return models.Comment.objects.filter(track_id=self.kwargs.get('pk'))


class StreamingFileView(views.APIView):
    """ Play a track """
    def set_play(self):
        self.track.plays_count += 1
        self.track.save()

    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk, private=False)
        if os.path.exists(self.track.file.path):
            self.set_play()
            response = HttpResponse('', content_type="audio/mpeg", status=206)
            response['X-Accel-Redirect'] = f"/mp3/{self.track.file.name}"
            return response
        else:
            return Http404


class DownloadTrackView(views.APIView):
    """download track"""
    def set_download(self):
        self.track.download += 1
        self.track.save()

    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk, private=False)
        if os.path.exists(self.track.file.path):
            self.set_download()
            response = HttpResponse('', content_type="audio/mpeg", status=206)
            response["Content-Disposition"] = f"attachment; filename={self.track.file.name}"
            response['X-Accel-Redirect'] = f"/media/{self.track.file.name}"
            return response
        else:
            return Http404


class StreamingFileAuthorView(views.APIView):
    """Play author's track"""
    permission_classes = [IsAuthor]

    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk, user=request.user)
        if os.path.exists(self.track.file.path):
            response = HttpResponse('', content_type="audio/mpeg", status=206)
            response['X-Accel-Redirect'] = f"/mp3/{self.track.file.name}"
            return response
        else:
            return Http404
