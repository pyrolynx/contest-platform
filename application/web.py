import functools
import json
import logging

import flask

import config
from application.models import Task, User, Solution

app = flask.Flask(__name__, template_folder=config.TEMPLATES_DIR)
app.config['UPLOAD_FOLDER'] = config.SOLUTIONS_FOLDER

@app.context_processor
def inject_user():
    return dict(user=getattr(flask.request, 'user', None))


def require_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = flask.request.cookies.get('session')
        try:
            user = User.get(token=token)
            setattr(flask.request, 'user', user)
            return func(*args, **kwargs, user=user)
        except User.DoesNotExist:
            return flask.redirect('/login?error=Auth required')
        except Exception:
            logging.error('error', exc_info=1)
            raise

    return wrapper


@app.route('/', methods=['GET'])
@require_auth
def index(user):
    return flask.render_template('index.html', tasks=Task.select())


@app.route('/login', methods=['GET', 'POST'])
def login():
    session_token = flask.request.cookies.get('session')
    if session_token and User.select().filter(token=session_token).count():
        return flask.redirect('/')

    if flask.request.method == 'GET':
        return flask.render_template('login.html')

    try:
        user = User.get(token=flask.request.form.get('token'))
    except User.DoesNotExist:
        return flask.redirect('/login?error=Invalid token')
    response = flask.redirect('/')
    response.set_cookie('session', user.token)

    return response


@app.route('/logout', methods=['GET'])
def logout():
    response = flask.redirect('/login')
    response.delete_cookie('session')
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        return flask.render_template('register.html')
    try:
        User.insert(token=flask.request.form['token'], username=flask.request.form['username']).execute()
        response = flask.redirect('/')
        response.set_cookie('session', flask.request.form['token'])
    except Exception:
        return flask.redirect('/register?error=Unknown error')
    return response


@app.route('/task/<int:task_id>', methods=['GET'])
@require_auth
def task_info(task_id: int, user):
    try:
        task = Task.get(id=task_id)
    except Task.DoesNotExist:
        return flask.redirect('/?error=Task not found')

    return flask.render_template('task.html', task=task)


@app.route('/task/<int:task_id>', methods=['POST'])
@require_auth
def task_submit(task_id, user):
    try:
        task = Task.get(id=task_id)
    except Task.DoesNotExist:
        return flask.redirect('/?error=Task not found')

    if not flask.request.files:
        return flask.redirect(f'/task/{task_id}?error=No solutions found in attachments')
    solution = flask.request.files['solution']
    if solution.content_type != 'text/x-python-script' or solution.filename.rsplit('.', 1)[-1].lower() != 'py':
        return flask.redirect(f'/task/{task_id}?error=Invalid content')
    solution = Solution.store(user, task, solution.read().decode())
    solution.run_tests()
    return flask.redirect('/scoreboard')


@app.route('/scoreboard', methods=['GET'])
@require_auth
def scoreboard(user):
    return flask.render_template('scoreboard.html',
                                 solutions=Solution.select().filter(user=user).order_by(Solution.submitted.desc()))


for file in (config.PROJECT_DIR / 'data' / 'tasks').iterdir():
    if file.is_dir() or file.name.rsplit('.', 1)[-1] != 'json':
        continue
    Task.insert(json.loads(file.read_text())).on_conflict('replace').execute()

app.run('0.0.0.0', debug=True)
