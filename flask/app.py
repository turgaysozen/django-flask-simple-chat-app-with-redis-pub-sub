from flask import (
    Flask,
    Response,
    redirect,
    render_template,
    request,
    session
)

import time
from datetime import datetime
import redis

app = Flask(__name__)
app.secret_key = 'app_secret'
redis = redis.Redis(host='redis', port=6379)

@app.route('/flask/')
def index():
    if 'user' not in session:
        return redirect('/flask/login')
    session["refreshed"] = True
    return render_template('chat.html', user=session['user'])


@app.route('/flask/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['user']
        return redirect('/flask')
    return render_template('login.html')


@app.route('/flask/post', methods=['POST'])
def post():
    message = request.form['message']
    user = session.get('user', 'anonymous')
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    redis.publish('chat', '[%s] - %s: %s' % (now, user, message))

    # Store the message in Redis cache
    message = '[%s] - %s: %s' % (now, user, message)
    added = redis.zadd('messages', {message: time.time()}, nx=True, ch=True)
    if added:
        redis.expire('messages', 600)  # set ttl to 10 mins
    return Response(status=204)


@app.route('/flask/stream')
def stream():
    if session.get("refreshed"):
        session["refreshed"] = False
        return Response(event_stream(refreshed=True), mimetype="text/event-stream")
    return Response(event_stream(refreshed=False), mimetype="text/event-stream")

def event_stream(refreshed):
    messages = redis.zrange('messages', 0, -1)
    if refreshed:
        for message in messages:
            yield 'data: %s\n\n' % message.decode('utf-8')

    pubsub = redis.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('chat')
    for pub_message in pubsub.listen():
        yield 'data: %s\n\n' % pub_message["data"].decode('utf-8')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
