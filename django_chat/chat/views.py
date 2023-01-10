from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse

import datetime
import redis
publisher = redis.Redis(host='redis', port=6379)


def index(request):
    if 'user' not in request.session:
        return redirect('/django/login')
    return render(request, 'chat.html', {'user': request.session['user']})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        request.session['user'] = request.POST.get('user')
        return redirect('/django')
    return render(request, 'login.html')


@csrf_exempt
def post(request):
    message = request.POST.get('message')
    user = request.session.get('user', 'anonymous')
    now = datetime.datetime.now().replace(microsecond=0).time()
    publisher.publish('chat', '[%s] - %s: %s' % (now.isoformat(), user, message))
    return HttpResponse(status=204)


def stream(request):
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def event_stream():
    pubsub = publisher.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('chat')
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data'].decode('utf-8')
