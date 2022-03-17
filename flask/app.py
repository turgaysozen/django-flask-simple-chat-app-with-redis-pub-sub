from flask import (
    Flask,
    Response,
    redirect,
    render_template,
    request,
    session,
)


import datetime
import redis


app = Flask(__name__)
app.secret_key = 'app_secret'
publisher = redis.Redis(host='redis', port=6379)


@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    return render_template('chat.html', user=session['user'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['user']
        return redirect('/')
    return render_template('login.html')


@app.route('/post', methods=['POST'])
def post():
    message = request.form['message']
    user = session.get('user', 'anonymous')
    now = datetime.datetime.now().replace(microsecond=0).time()
    publisher.publish('chat', '[%s] - %s: %s' % (now.isoformat(), user, message))
    return Response(status=204)


@app.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")


def event_stream():
    pubsub = publisher.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('chat')
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data'].decode('utf-8')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
