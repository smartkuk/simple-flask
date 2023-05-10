import argparse
from json import JSONEncoder
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import pprint
from typing import Dict
from flask import Flask, jsonify,  abort, redirect, render_template, url_for
from flask import request
from os import environ

app = Flask(__name__)
VERSION = "BLUE" if "VERSION" not in environ else environ["VERSION"]
CONTEXT_PATH = environ["CONTEXT_PATH"] if "CONTEXT_PATH" in environ else "/"
PORT = environ["PORT"] if "PORT" in environ else 5001
VERBOSE = False
if "VERBOSE" in environ:
    if environ["VERBOSE"] == "True":
        VERBOSE = True
ENABLE_ARGS = False
ARGS = {}


class User:
    def __init__(self, **kwargs):
        self._user_id: str = None
        self._user_name: str = None
        self._country: str = None

        if "user_id" in kwargs:
            self._user_id = kwargs["user_id"]
        if "user_name" in kwargs:
            self._user_name = kwargs["user_name"]
        if "country" in kwargs:
            self._country = kwargs["country"]

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

    @property
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, value: str):
        self._country = value

    def __str__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def serialize(self) -> dict:
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "country": self.country
        }


class SimpleJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return obj.serialize()
        return super(SimpleJSONEncoder, self).default(obj)


app.json_encoder = SimpleJSONEncoder


USERS: Dict[str, User] = {}


@app.route("/")
def render_page():
    return render_template("index.html", users=[user for _, user in USERS.items()], version=VERSION, envs=[{"key": k, "value": v} for k, v in environ.items()])


@app.route("/health")
def get_health_check():
    if ENABLE_ARGS is True:
        return jsonify({"status": "OK", "version": VERSION, "arguments": ARGS})
    return jsonify({"status": "OK", "version": VERSION})


@app.route("/header")
def get_header():
    data = {"version": VERSION}
    if ENABLE_ARGS is True:
        data["arguments"] = ARGS
    for key in request.headers.keys():
        data[key] = request.headers.get(key, "")
    return jsonify(data)


@app.route("/users", methods=["POST"])
def create_user():
    app.logger.debug(f"request: {request}")
    if request.is_json is True:

        data = request.get_json()
        user = User(**data)
        USERS[user.user_id] = user

        return jsonify(user), 200

    if "userId" in request.form and "userName" in request.form:
        app.logger.info(f"request.form => {request.form}")
        user = User(user_id=request.form['userId'],
                    user_name=request.form['userName'],
                    country=request.form['country'])
        USERS[user.user_id] = user

        return redirect(url_for("render_page"))

    abort(400, "Http header application/json is required")


@app.route("/users", methods=["GET"], defaults={"user_id": None})
@app.route("/users/<user_id>", methods=["GET"])
def get_users(user_id: str):
    if user_id:
        if user_id in USERS:
            result = {"user": USERS[user_id], "version": VERSION}
            if ENABLE_ARGS is True:
                result["arguments"] = ARGS
            return jsonify(result), 200
        return jsonify(message=f"Not found user by user_id={user_id}"), 404

    if "user_name" in request.args:
        user_name = request.args.get('user_name')
        for _, user in USERS.items():
            if user.user_name == user_name:
                result = {"user": user, "version": VERSION}
                if ENABLE_ARGS is True:
                    result["arguments"] = ARGS
                return jsonify(result), 200
        return jsonify(message=f"Not found user by user_name={user_name}"), 404

    result = {"users": [user for _, user in USERS.items()], "version": VERSION}
    if ENABLE_ARGS is True:
        result["arguments"] = ARGS
    return jsonify(result), 200


@app.route("/users/<user_id>", methods=["DELETE"])
def remove_user(user_id: str):
    if user_id in USERS:
        user = USERS[user_id]
        del USERS[user_id]
        return jsonify(user), 200

    return jsonify(message=f"Not found user by user_id={user_id}"), 404


def validate_context_path(context_path: str) -> bool:

    if context_path != "":

        if not context_path.startswith("/"):
            raise ValueError(
                f"Context path must start with '/' string.(CONTEXT_PATH: {context_path})")

        if len(context_path) != 1 and context_path.endswith("/"):
            raise ValueError(
                f"Context path must not end with '/' string.(CONTEXT_PATH: {context_path})")


def prepare_users():
    return {
        "1": User(user_id="1", user_name="Trump", country="US"),
        "2": User(user_id="2", user_name="Obama", country="US"),
        "3": User(user_id="3", user_name="Biden", country="US"),
        "4": User(user_id="4", user_name="Jefferson", country="US"),
        "5": User(user_id="5", user_name="Kennedy", country="US"),
    }


@app.before_request
def verbose():
    if VERBOSE is True:
        app.logger.info(f"request: {request}")
        app.logger.info(f"request path: {request.path}")

    if request.path is None or request.path == "":
        return redirect(url_for("render_page"))


@app.after_request
def add_header(response):
    response.headers['version'] = VERSION
    return response


if __name__ == "__main__":
    validate_context_path(CONTEXT_PATH)

    parser = argparse.ArgumentParser(
        prog='Simple-Flask', description='Web application for testing')
    parser.add_argument("--enable", action="store_true",
                        help="Enable to print and response arguments from user inputs")
    parser.add_argument("--version", type=str,
                        help="Just version for print and response")
    parser.add_argument("--owner", type=str,
                        help="Just owner for print and response")
    args = parser.parse_args()

    USERS = prepare_users()

    app.debug = True
    ENABLE_ARGS = args.enable
    if ENABLE_ARGS is True:
        app.logger.info(f"Enable ARGS => {args}")
        if args.version:
            ARGS["version"] = args.version
        if args.owner:
            ARGS["owner"] = args.owner

    app.logger.info(f"""
Env List
VERSION      : {VERSION}
VERBOSE      : {VERBOSE}
CONTEXT_PATH : {CONTEXT_PATH}
PORT         : {PORT}""")

    if CONTEXT_PATH and CONTEXT_PATH != "/":
        app.wsgi_app = DispatcherMiddleware(app, {CONTEXT_PATH: app.wsgi_app})
    app.run(host='0.0.0.0', port=PORT, debug=True)
