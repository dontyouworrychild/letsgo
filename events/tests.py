from rest_framework.test import APITestCase
from django.test import Client
from rest_framework import status
from .models import Event, Category, BookedEvent
from users.models import User
from .serializers import BookedEventSerializer


class CategoryViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="lmoyer",
            password="password"
        )

        cls.category = Category.objects.create(
            name='Fun')

    def setUp(self):
        login_url = '/login/'
        self.client = Client()
        response = self.client.post(login_url, data={"username": "lmoyer", "password": "password"})
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {response.data["access"]}'

    def test_get_list(self):
        url = '/api/v1/categories/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, self.category)

    def test_get_individual_model(self):
        url = f'/api/v1/categories/{self.category.id}/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Fun')

    def test_get_nonexistent_model(self):
        url = '/api/v1/categories/3/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_data(self):
        url = '/api/v1/categories/'
        data = {"name": 'Title 2'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_resource_invalid_data(self):
        url = '/api/v1/categories/'
        data = {"title": 'Title 2'}   # Invalid data

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_nonexistent_resource(self):
        url = '/api/v1/categories/5/'

        response = self.client.patch(url, {'name': 'Updated Model'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_wrong_data(self):
        url = f'/api/v1/categories/{self.category.id}/'

        response = self.client.patch(url, {'username': 'Updated Model'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_individual_model(self):
        url = f'/api/v1/categories/{self.category.id}/'

        response = self.client.patch(url, {'name': 'Fun 2'})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_nonexistent_resource(self):
        url = '/api/v1/categories/5/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_model(self):
        url = f'/api/v1/categories/{self.category.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class EventViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="lmoyer",
            password="password"
        )

        cls.event = Event.objects.create(
            title='Title',
            description="Description",
            price=15,
            created_by=cls.user,
            seats=100)

    def setUp(self):
        login_url = '/login/'
        self.client = Client()
        response = self.client.post(login_url, data={"username": "lmoyer", "password": "password"})

        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {response.data["access"]}'

    def test_get_list(self):
        url = '/api/v1/events/'

        # Perform a GET request to the API Events view
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, self.event)

    def test_get_individual_model(self):
        url = f'/api/v1/events/{self.event.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Title')
        self.assertEqual(response.data['description'], "Description")
        # self.assertEqual(response.data['created_by'], self.user.id)
        self.assertEqual(response.data['seats'], 100)
        self.assertEqual(response.data['price'], 15)

    def test_get_nonexistent_model(self):
        url = '/api/v1/events/16/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_data(self):
        Category.objects.create(name='Category-3')
        Category.objects.create(name='Category-4')
        url = '/api/v1/events/'
        data = {
            "title": 'Title 2',
            "description": "Description 2",
            "price": 25,
            "seats": 200,
            "event_type": "public",
            "guests": [self.user.id],
            "categories": [3, 4]
        }
        # Perform a POST request to the API view
        response = self.client.post(url, data)

        # Assert that the response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Title 2')
        self.assertEqual(response.data['description'], "Description 2")
        self.assertEqual(response.data['seats'], 200)
        self.assertEqual(response.data['price'], 25)
        self.assertEqual(response.data['event_type'], 'public')
        self.assertEqual(response.data['categories'], [3, 4])

    def test_post_resource_invalid_data(self):

        url = '/api/v1/events/'
        data = {"name": 'Title 2',
                'field': 'non existing field',
                "description": "Description 2",
                "price": 25,
                }   # Invalid data
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_nonexistent_resource(self):
        url = '/api/v1/events/15/'
        response = self.client.patch(url, {'title': 'Updated Model'}, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_wrong_data(self):
        url = f'/api/v1/events/{self.event.id}/'
        response = self.client.patch(url, {'price': 'atyrau'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.patch(url, {'event_type': 'private'}, content_type='application/json')
        self.assertNotIn('event_type', response.json())

    def test_patch_individual_model(self):
        url = f'/api/v1/events/{self.event.id}/'
        response = self.client.patch(url, {'title': 'Updated Model'}, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Model')
        self.assertEqual(response.data['description'], "Description")
        # self.assertEqual(response.data['created_by'], self.user.id)
        self.assertEqual(response.data['seats'], 100)
        self.assertEqual(response.data['price'], 15)

    def test_delete_nonexistent_resource(self):
        url = '/api/v1/events/5/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_model(self):
        url = f'/api/v1/events/{self.event.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BookedEventViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="lmoyer",
            password="password"
        )

        cls.event = Event.objects.create(
            title='Title',
            description="Description",
            price=15,
            created_by=cls.user,
            seats=100)

        cls.bookedevent = BookedEvent.objects.create(
            user=User.objects.first(),
            event=cls.event,
            status="registered"
        )

    def setUp(self):
        login_url = '/login/'
        self.client = Client()
        response = self.client.post(login_url, data={"username": "lmoyer", "password": "password"})

        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {response.data["access"]}'

    def test_get_list(self):
        url = '/api/v1/booked_events/'

        response = self.client.get(url)
        serialized_bookedevent = BookedEventSerializer(self.bookedevent).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # Assert that the serialized bookedevent object is present in the response data
        self.assertIn(serialized_bookedevent, response.data)

    def test_get_individual_model(self):
        url = f'/api/v1/booked_events/{self.bookedevent.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data['user'], User.objects.first().id)
        self.assertEqual(response.data['event'], self.event.id)
        self.assertEqual(response.data['status'], 'registered')

    def test_get_nonexistent_model(self):
        url = '/api/v1/booked_events/4/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_data(self):
        url = '/api/v1/booked_events/'
        event = Event.objects.create(
            title='title',
            description="Description",
            price=15,
            created_by=self.user,
            seats=100)
        data = {"event": event.id}

        # Perform a POST request to the API view
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.data['booked_event']['user'], self.user.id)
        self.assertEqual(response.data['booked_event']['event'], event.id)

    def test_post_resource_invalid_data(self):
        url = '/api/v1/booked_events/'
        data = {
            "event": "5a"  # Invalid data
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "name": "hello",
            "event": "6"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_nonexistent_resource(self):
        url = '/api/v1/booked_events/100/'
        response = self.client.patch(url, {'status': 'participated'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_wrong_data(self):
        url = f'/api/v1/booked_events/{self.bookedevent.id}/'

        response = self.client.patch(url, {'event': 2}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(url, {'status': 'mama'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(url, {'status': 'participated', 'user': 2}, content_type='application/json')
        self.assertNotIn('user', response.json())

    def test_patch_individual_model(self):
        url = f'/api/v1/booked_events/{self.bookedevent.id}/'
        response = self.client.patch(url, {'status': 'participated'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'participated')

    def test_delete_nonexistent_resource(self):
        url = '/api/v1/booked_events/5/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_model(self):
        url = f'/api/v1/booked_events/{self.bookedevent.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
