from rest_framework import serializers
from .models import BookedEvent, Event, Category, Rating
from rest_framework.exceptions import ValidationError


class EventSerializer(serializers.ModelSerializer):
    '''
        For POST, GET
    '''
    rating = serializers.DecimalField(default=0, max_digits=3, decimal_places=2, read_only=True)
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'price', 'start_time', 'created_by', 'guests', 'event_type', 'rating',
                  'seats', 'categories')


class EventUpdateSerializer(serializers.ModelSerializer):
    '''
        For PATCH
    '''
    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'price', 'start_time', 'guests', 'seats', 'categories')


class BookedEventSerializer(serializers.ModelSerializer):
    '''
        for POST, GET
    '''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BookedEvent
        fields = ('id', 'event', 'user', 'status')


class BookedEventUpdateSerializer(serializers.ModelSerializer):
    '''
        for PATCH

        WORK ON THIS: it is returning a list of errors,
        but I need to return only a single error
        In this format:
        {"error": "You did not include status in the request"}
    '''
    class Meta:
        model = BookedEvent
        fields = ('id', 'status')

    def validate(self, attrs):
        if self.context['request'].method == 'PATCH' and 'status' not in attrs:
            raise ValidationError({'error': "You did not include the status"})
            # raise serializers.ValidationError({'error': 'You did not include status in the request'})
        return attrs


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Rating
        fields = ('id', 'user', 'event', 'score')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
