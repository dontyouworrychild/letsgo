from django.core.management.base import BaseCommand
import random
from faker import Faker
from django.contrib.auth import get_user_model
# from django.db import connection as django_connection
from users.models import FriendRequest
from events.models import Event, BookedEvent, Category
from users.choices import FriendRequestStatus
from events.choices import *
import requests
import concurrent.futures
import json


# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry


# session = requests.Session()
# retry = Retry(connect=3, backoff_factor=0.5)
# adapter = HTTPAdapter(max_retries=retry)
# session.mount('http://', adapter)
# session.mount('https://', adapter)

class Command(BaseCommand):
    help = 'Populate the database with dummy data'

    def handle(self, *args, **options):
        # Your script code goes here
        fake = Faker()
        User = get_user_model()

        # Create dummy users

        users = []
        # users = User.objects.all()
        users_username = set()
        for _ in range(1500):
            username = fake.user_name()
            email = f"{username}@gmail.com"
            password = "password"
            if username not in users_username:
                User.objects.create_user(username=username, email=email, password=password)
                users_username.add(username)
            # users.append(user)
        users = User.objects.all()

        # Create categories
        categories = [
            'Category 1',
            'Category 2',
            'Category 3',
            'Category 4',
            'Category 5',
            'Category 6',
            'Category 7',
            'Category 8',
            'Category 9',
            'Category 10',
            'Category 11',
            'Category 12',
            'Category 13',
            'Category 14',
            'Category 15',
            'Category 16',
            'Category 17',
            'Category 18',
            'Category 19',
            'Category 20',
            'Category 21',
            'Category 22',
            'Category 23',
            'Category 24',
        ]

        for category_name in categories:
            category = Category.objects.create(name=category_name)

        # categories = Category.objects.all()

        # Create events
        events = []
        # events = Event.objects.all()
        # categories = Category.objects.all()

        '''
        '''

        for _ in range(2000):
            title = fake.word()
            description = fake.sentence()
            price = random.randint(0, 100)
            created_by = random.choice(users)
            event_type = random.choice(EventType.values)
            event = Event.objects.create(
                title=title,
                description=description,
                price=price,
                created_by=created_by,
                event_type=event_type,
                seats=random.randint(1, 100)
            )
            event_categories = []
            for _ in range(5):
                current_category_id = random.randint(1, 24)
                if current_category_id not in event_categories:
                    category = Category.objects.filter(id=current_category_id).first()
                    event.categories.add(category)
                    event_categories.append(current_category_id)

        # current_category = random.choice(categories)
        # if current_category not in event_categories:
        # event.categories.set(current_category)
        # event_categories.append(current_category)
        # event.categories.set()
        # event.categories.set(random.sample(list(Category.objects.all()), random.randint(1, 3)))
        # events.append(event)

        # title = fake.word()
        # description = fake.sentence()
        # price = 1000
        # created_by = random.choice(users)
        # event_type = 'public'
        # event = Event.objects.create(
        #     title=title,
        #     description=description,
        #     price=price,
        #     created_by=created_by,
        #     event_type=event_type,
        #     seats=1
        # )
        # auth_users = []
        # auth_url = 'http://127.0.0.1:8000/login/'
        # url = 'http://127.0.0.1:8000/api/v1/booked_events/'

        # # session.get(auth_url)

        # for user in users:
        #     data = {
        #         'username': user.username,
        #         'password': 'password',
        #     }
        #     print(data)
        #     response = requests.post(auth_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        #     # print(response.json()['access'])
        #     auth_users.append(response.json()['access'])
        # def book_event(user_id):
        #     data = {
        #         'event': 1
        #     }
        #     # print(auth_users[user_id])
        #     # return auth_users[user_id]
        #     # f"Bearer {auth_users[user_id]}"
        #     response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {auth_users[user_id]}'})
        #     return response.json()

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     futures = [executor.submit(book_event, user_id) for user_id in range(len(users))]

        #     # Wait for all the requests to complete
        #     concurrent.futures.wait(futures)

        #     # Retrieve the results
        #     results = [future.result() for future in futures]

        # for user_id, result in zip(users, results):
        #     print(f"User {user_id} - {result}")

        events = Event.objects.all()
        for user in users:
            for _ in range(random.randint(0, 20)):
                friend_id = random.randint(1, len(users))
                # friend_id = random.randint(1, 24)
                if friend_id != user.id:
                    # friend = random.choice(users)
                    friend = User.objects.filter(id=friend_id).first()
                    if friend not in user.friends.all():
                        user.friends.add(friend)
                # friend = User.objects.all(id=user_id)
                # if friend.id != user.id:
                    # if friend not in user.friends.all():
                    # user.friends.add(friend)

        # # Create booked events
        # print(f"users len: {len(users)}")
        # print(f"events len: {len(events)}")

        for user in users:
            for _ in range(random.randint(0, 30)):
                event_id = random.randint(1, len(events))
                # event_id = random.choice(events)
                event = Event.objects.filter(id=event_id).first()
                # event = Event.objects.all(id=event_id)
                if event.event_type == 'public':
                    BookedEvent.objects.create(user=user, event=event, status='registered')
                if event.event_type == 'private' and user in event.created_by.friends.all():
                    BookedEvent.objects.create(user=user, event=event, status='registered')

        users = User.objects.all()
        # Create friend requests
        for user in users:
            for _ in range(random.randint(0, 15)):
                receiver_id = random.randint(1, len(users))
                receiver = User.objects.filter(id=receiver_id).first()

                if receiver_id != user.id and receiver not in user.friends.all():
                    FriendRequest.objects.create(
                        sender=user, receiver=receiver, status=FriendRequestStatus.PENDING)

        # print("Database population completed.")

        # Retrieve all users
        users = User.objects.all()
        print(f"user len: {len(users)}")
        # print([user.username for user in users])
        # print("Users:")
        # for user in users:
        #     print(user.username)

        # Retrieve all events
        events = Event.objects.all()
        print(f"events len: {len(events)}")
        # print(len(events))
        # print("Events:")
        # for event in events:
        #     print(event.title)

        # Retrieve all categories
        categories = Category.objects.all()
        print(f"categories len: {len(categories)}")
        # print(len(categories))
        # print("Categories:")
        # for category in categories:
        #     print(category.name)

        # Retrieve all booked events
        booked_events = BookedEvent.objects.all()
        print(f"booked_events len: {len(booked_events)}")
        # print(len(booked_events))
        # print("Booked Events:")
        # for booked_event in booked_events:
        #     print(f"User: {booked_event.user.username}, Event: {booked_event.event.title}, Status: {booked_event.status}")

        # Retrieve all friend requests
        friend_requests = FriendRequest.objects.all()
        print(f"friend_requests len: {len(friend_requests)}")
        # print(len(friend_requests))
        # print("Friend Requests:")
        # for friend_request in friend_requests:
        #     print(f"Sender: {friend_request.sender.username}, Receiver: {friend_request.receiver.username}, Status: {friend_request.status}")
