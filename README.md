## Letsgo

Event
- check for all public events (everyone can register) and private events (only creator's friends can register).
- create private events
- send a request to the admins to get access to show your event publicly (to create public event)
- if you register for paid event, after payment you will receive an email (used celery).
- give a rating only to the participated events


User
- user authentication
- send or accept/decline friend request
- permissions

## Development

1. Install docker
2. Copy .env.example and rename the copy to .env

```
docker-compose up --build
```

In another terminal:
```
docker-compose run letsgo sh -c "python manage.py makemigrations"
docker-compose run letsgo sh -c "python manage.py migrate"
```

You can use a script to generate users, events, categories, friend request, booked events. 
It is located in letsgo/fillers/management/commands/scripts.py
```
docker-compose run letsgo sh -c "python manage.py scripts"
```

3. Install Postman https://www.postman.com/downloads/ or some other tools to test the API


# Comment
- I am not sure whether it is a good practice to leave the logging tool or not, so after each request you will see all SQL commands that was used for the request 

I will really appreciate any suggestions that you can give to me either on improving the code, improving the test, using some tools or adding new features.
<br> You can text me: duke.imeket@gmail.com <br>
or via Reddit: https://www.reddit.com/user/RadiantPersonality58


