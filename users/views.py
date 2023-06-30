from django.db.models import (Q, Prefetch)
from rest_framework import exceptions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from common.exceptions import ApiException
from .serializers import FriendSerializer, UserSerializer, FriendRequestSerializer
from .models import User, FriendRequest
from .permissions import IsFriendRequestSenderOrReceiver
from .parameters import get_event_list_parameter


@extend_schema(tags=['Users'])
class UserViewSet(ModelViewSet):
    queryset = User.objects.prefetch_related(
        Prefetch('friends', queryset=User.objects.all().only('id'))
    )
    serializer_class = UserSerializer


@extend_schema(tags=['Friend Request'])
class FriendRequestViewSet(ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsFriendRequestSenderOrReceiver]

    def get_queryset(self):
        queryset = self.queryset
        section_params = self.request.query_params.get('section', "receiver")

        if section_params == 'sender':
            queryset = queryset.filter(sender=self.request.user)
        elif section_params == 'receiver':
            queryset = queryset.filter(receiver=self.request.user)

        return queryset

    @extend_schema(
        parameters=get_event_list_parameter,
        responses={200: FriendRequestSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        sender_id = request.user.id
        receiver_id = request.data.get('receiver')

        if sender_id == receiver_id:
            raise ApiException({'error': "Invalid request to yourself"})

        sender = User.objects.get(id=sender_id)
        if sender.friends.filter(id=receiver_id).exists():
            raise ApiException({'error': "You are already friends"})

        if self.queryset.filter(Q(sender=sender_id, receiver=receiver_id) |
                                Q(sender=receiver_id, receiver=sender_id)).exists():
            raise ApiException(
                {'error': 'You or the person you want to be a friend already made a request or are friends'})

        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        friend_request = self.get_object()
        sender = friend_request.sender
        receiver = friend_request.receiver

        if request.data['status'] == 'accepted':
            sender.friends.add(receiver)
            self.destroy(request, *args, **kwargs)
            return Response({"message": "Friend request have been accepted"})

        if request.data['status'] == 'declined':
            self.destroy(request, *args, **kwargs)
            return Response({"message": "Friend request have been declined"})


@extend_schema(tags=['Friends'])
class FriendViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ('get', )

    @extend_schema(
        parameters=get_event_list_parameter,
        responses={200: FriendSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        user_id = self.request.query_params.get('id', self.request.user.id)

        try:
            user = self.queryset.only('id').get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.NotFound(f"{user_id} not found")
        queryset = user.friends.only('id', 'username', 'first_name', 'last_name')

        return queryset
