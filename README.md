This is a server to server chat application build with Django and Flask.
These 2 server applications can chat with each other on the public channel by 
``` redis PUB/SUB - https://redis.io/topics/pubsub ```.

To start application run the following command:
```
docker-compose up --build
```

Go to -> ``` http://127.0.0.1:8000/``` for Django app </br>
Go to -> ``` http://127.0.0.1:8001/``` for Flask app

Enter username and send message.

Also, if you have installed ```ngrok``` on your system, you can make public accessible 
one of the app server and connect with anywhere on the internet, can share with your friend 
and chat with them.

For more info about ```ngrok```, go to ```https://ngrok.com/```.
