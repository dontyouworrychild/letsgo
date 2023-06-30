from rest_framework import serializers
from .models import User, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    # password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'friends')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

    def create(self, validated_data):
        raise serializers.ValidationError("Creation not allowed for this serializer")


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FriendRequest
        fields = ('id', 'receiver', 'sender', 'status')
