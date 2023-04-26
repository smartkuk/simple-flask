from json import JSONEncoder
import pprint
from typing import Dict
from flask import Flask, jsonify,  abort, render_template
from flask import request
from os import environ

app = Flask(__name__)


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)

        start_response('404', [('Content-Type', 'text/plain')])
        return ["This url does not belong to the app.".encode()]


class User:
    def __init__(self, **kwargs):
        self._user_id: str = None
        self._user_name: str = None

        if "user_id" in kwargs:
            self._user_id = kwargs["user_id"]
        if "user_name" in kwargs:
            self._user_name = kwargs["user_name"]

    @property
    def user_id(self) -> str:
        return self._user_id

    @user_id.setter
    def user_id(self, value: str):
        self._user_id = value

    @property
    def user_name(self) -> str:
        return self._user_name

    @user_name.setter
    def user_name(self, value: str):
        self._user_name = value

    def __str__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def serialize(self) -> dict:
        return {
            "user_id": self.user_id,
            "user_name": self.user_name
        }


class SimpleJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return obj.serialize()
        return super(SimpleJSONEncoder, self).default(obj)


app.json_encoder = SimpleJSONEncoder

USERS: Dict[str, User] = {}


@app.route("/")
def hello_world():
    return render_template("index.html", users=[user for _, user in USERS.items()])


@app.route("/health")
def get_health_check():
    return jsonify({"status": "OK"})


@app.route("/header")
def get_header():
    data = {}
    for key in request.headers.keys():
        data[key] = request.headers.get(key, "")
    return jsonify(data)


@app.route("/users", methods=["POST"])
def create_user():
    app.logger.debug(f"request: {request}")
    if request.is_json is False:
        abort(400, "Http header application/json is required")

    data = request.get_json()
    user = User(**data)
    USERS[user.user_id] = user

    return jsonify(user), 200


@app.route("/users", methods=["GET"], defaults={"user_id": None})
@app.route("/users/<user_id>", methods=["GET"])
def get_users(user_id: str):
    if user_id:
        if user_id in USERS:
            return jsonify(USERS[user_id]), 200
        return jsonify(message=f"Not found user by user_id={user_id}"), 404

    if "user_name" in request.args:
        user_name = request.args.get('user_name')
        for _, user in USERS.items():
            if user.user_name == user_name:
                return jsonify(user), 200
        return jsonify(message=f"Not found user by user_name={user_name}"), 404

    return jsonify([user for _, user in USERS.items()]), 200


@app.route("/users/<user_id>", methods=["DELETE"])
def remove_user(user_id: str):
    if user_id in USERS:
        user = USERS[user_id]
        del USERS[user_id]
        return jsonify(user), 200

    return jsonify(message=f"Not found user by user_id={user_id}"), 404


def validate_context_path(context_path: str) -> bool:

    if not context_path.startswith("/"):
        raise ValueError(
            f"Context path must start with '/' string.(CONTEXT_PATH: {context_path})")

    if len(context_path) != 1 and context_path.endswith("/"):
        raise ValueError(
            f"Context path must not end with '/' string.(CONTEXT_PATH: {context_path})")


def prepare_users():
    return {
        "1": User(user_id="1", user_name="Trump"),
        "2": User(user_id="2", user_name="Obama"),
        "3": User(user_id="3", user_name="Biden"),
    }


if __name__ == "__main__":

    app.debug = True
    app.wsgi_app = PrefixMiddleware(app.wsgi_app)

    if "CONTEXT_PATH" in environ:

        validate_context_path(environ['CONTEXT_PATH'])

        app.wsgi_app = PrefixMiddleware(
            app.wsgi_app, prefix=environ["CONTEXT_PATH"])
        app.logger.info(
            f"Configured Env CONTEXT_PATH: {environ['CONTEXT_PATH']}")

    port = environ["PORT"] if "PORT" in environ else 5001
    USERS = prepare_users()

    app.logger.info(f"Expose port number {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
