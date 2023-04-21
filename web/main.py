import logging
from flask import Flask, jsonify, make_response
from flask import request
from os import environ

CONTEXT_PATH="/"
if "CONTEXT_PATH" in environ:
    context_path = environ["CONTEXT_PATH"]
    logging.info(f"Using CONTEXT_PATH -> {context_path}")

class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]

app = Flask(__name__)
app.debug = True
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=CONTEXT_PATH)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/health")
def get_health_check():
    return jsonify({"status": "OK"})

@app.route("/header")
def get_header():
    data = {}
    for key in request.headers.keys():
        data[key] = request.headers.get(key, "")
    # return make_response(jsonify(request.headers), 200)
    return jsonify(data)
    
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5001', debug=True)