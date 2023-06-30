import os
import stripe
from django.db import transaction
from django.db.models import (Avg, Q, Prefetch)
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from users.models import User
from common.exceptions import ApiException
from common.paginations import StandardResultsSetPagination
from .models import Event, BookedEvent, Category, Rating
from .serializers import (
    BookedEventUpdateSerializer,
    EventSerializer,
    EventUpdateSerializer,
    CategorySerializer,
    BookedEventSerializer,
    RatingSerializer,
)
from .permissions import IsEventOwner, IsBookedEventOwner
from .tasks import send_payment_confirmation
from .parameters import get_event_list_parameter

stripe.api_key = os.environ.get('STRIPE_API_KEY')


@extend_schema(tags=['Events'])
class EventViewSet(ModelViewSet):
    queryset = Event.objects.select_related('created_by').prefetch_related(
        Prefetch('guests', queryset=User.objects.all().only('username', 'first_name', 'last_name')),
        Prefetch('categories', queryset=Category.objects.all()),
    )
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        permission_classes = [AllowAny]
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsEventOwner]

        return [permission() for permission in permission_classes]

    @extend_schema(
        parameters=get_event_list_parameter,
        responses={200: EventSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return EventUpdateSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        queryset = self.queryset

        search_query = self.request.query_params.get('search')
        privacy_filter = self.request.query_params.get('event_type', 'public')
        sort_order = self.request.query_params.get('sort_by')
        category_list_filter = self.request.query_params.getlist('category')
        relation_filter = self.request.query_params.get('relation', 'all')

        # Apply privacy field filter
        if privacy_filter:
            if self.request.user.is_authenticated:
                queryset = queryset.filter(event_type=privacy_filter).filter(
                    created_by__in=self.request.user.friends.all())
            else:
                queryset = queryset.filter(event_type="public")

        queryset = queryset.annotate(rating=Avg('ratings__score'))

        if category_list_filter:
            queryset = queryset.filter(categories__in=category_list_filter)

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(created_by__username__icontains=search_query)
            )

        if relation_filter != 'all':
            user = self.request.user
            if relation_filter != 'user':
                queryset = queryset.filter(created_by=user)
            elif relation_filter != 'friends':
                queryset = queryset.filter(created_by__friends=user, created_by__friends__private=False)

        # Apply sorting
        if sort_order:
            # According to price
            if sort_order == 'price-asc':
                queryset = queryset.order_by('price')
            elif sort_order == 'price-desc':
                queryset = queryset.order_by('-price')
            # According to other fields that will be added in the future

        return queryset


@extend_schema(tags=['Booked Events'])
class BookedEventViewSet(ModelViewSet):
    queryset = BookedEvent.objects.all()
    serializer_class = BookedEventSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ('post', 'patch', 'get')

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ['partial_update', 'update', 'retrieve']:
            permission_classes += [IsBookedEventOwner]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return BookedEventUpdateSerializer

        return super().get_serializer_class()

    @transaction.atomic
    def create(self, request):
        booking_serializer = BookedEventSerializer(data=request.data, context={'request': request})
        booking_serializer.is_valid(raise_exception=True)

        user = request.user
        event_id = request.data.get('event', None)

        if self.queryset.only('user', 'event').filter(user=user, event=event_id).exists():
            raise ApiException({'error': 'You already booked this event'})

        event = get_object_or_404(Event, pk=event_id)
        if event.event_type == 'private' and user not in event.created_by.friends.all():
            raise ApiException(
                {'error': 'You can not book this event, it is private event, whose author is not your friend'})

        # Beginning of transaction
        payment_intent = None
        with transaction.atomic():
            if event.seats <= event.booked_events.count():
                raise ApiException(
                    {'error': 'No seats available for this event'})
            if event.price > 0:
                payment_intent = self.create_payment_intent(event, user)
            booking_serializer.save()
            # End of transaction

        if payment_intent:
            send_payment_confirmation.delay(user.id)

        return Response({
            'booked_event': booking_serializer.data,
            'client_secret': payment_intent.client_secret if payment_intent else None,
        }, status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, *args, **kwargs):
        booked_event = get_object_or_404(BookedEvent, pk=kwargs.get('pk'))
        book_event_request_status = request.data.get('status', None)

        if booked_event.status == 'participated':
            raise ApiException(
                {'error': 'You can update only the registered event'})

        if book_event_request_status == 'registered' and booked_event.status == 'registered':
            raise ApiException(
                {'error': 'You have already registered for this event'})

        if book_event_request_status == 'unregistered':
            # Return his money back
            booked_event.delete()
            return Response(
                {'message': 'You have unregistered from the event'},
                status=status.HTTP_200_OK)

        return super().partial_update(request, *args, **kwargs)

    def create_payment_intent(self, event, user):
        return stripe.PaymentIntent.create(
            amount=event.price * 100,
            currency='usd',
            automatic_payment_methods={'enabled': True},
            metadata={'event_id': event.id, 'user_id': user.id},
        )


@extend_schema(tags=['Rating'])
class RatingViewSet(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ('post', 'get')

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request):
        serializer = RatingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        event_id = request.data.get('event', None)

        if self.queryset.only('user', 'event').filter(user=user, event=event_id).exists():
            raise ApiException({'error': 'You already gave a rating to this event'})

        if BookedEvent.objects.filter(user=user, event_id=event_id).exists():
            request.data['user'] = user.id
            return super().create(request)

        raise ApiException({'error': 'You did not participate in this event'})


@extend_schema(tags=['Category'])
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ('post', 'get')
