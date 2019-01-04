from flask import Flask, request
from flask import jsonify
import json
import os
import copy
import pprint

app = Flask(__name__)

class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, resp):
        errorlog = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(environ, log_response)

def show_request(req):
    try:
        print('\nSHOW REQUEST START')
        print('request.path: {0}'.format(req.path))
        print('request.full_path: {0}'.format(req.full_path))
        print('request.script_root: {0}'.format(req.script_root))
        print('request.url: {0}'.format(req.url))
        print('request.base_url: {0}'.format(req.base_url))
        print('request.url_root: {0}'.format(req.url_root))
        print('request.args: {0}'.format(req.args))
        print('request.authorization: {0}'.format(req.authorization))
        print('request.content_type: {0}'.format(req.content_type))
        print('request.cookies: {0}'.format(req.cookies))
        print('request.data: {0}'.format(req.data))
        print('request.endpoint: {0}'.format(req.endpoint))
        print('request.form: {0}'.format(req.form))
        print('request.form_data_parser_class: {0}'.format(req.form_data_parser_class))
        print('request.get_data(): {0}'.format(req.get_data()))
        print('request.get_json(): {0}'.format(req.get_json()))
        print('request.headers: {0}'.format(req.headers))
        print('request.host: {0}'.format(req.host))
        print('request.host_url: {0}'.format(req.host_url))
        print('request.is_secure: {0}'.format(req.is_secure))
        print('request.json: {0}'.format(req.json))
        print('request.method: {0}'.format(req.method))
        print('request.query_string: {0}'.format(req.query_string))
        print('request.referrer: {0}'.format(req.referrer))
        print('request.remote_addr: {0}'.format(req.remote_addr))
        print('request.remote_user: {0}'.format(req.remote_user))
        print('request.scheme: {0}'.format(req.scheme))
        print('request.url_rule: {0}'.format(req.url_rule))
        print('request.user_agent: {0}'.format(req.user_agent))
        print('request.view_args: {0}'.format(req.view_args))
        print('SHOW REQUEST END\n')
    except Exception as e:
        print(e)
        print('Failed to show_request')


@app.route('/', methods=['GET'])
def hello_world():
    #show_request(request)
    return jsonify({
        'HOSTNAME': os.environ['HOSTNAME'],
        'HOME': os.environ['HOME'],
        'MESSAGE': 'ping'
    })

def get_jsonify_request(req):
    return jsonify({
        'request_path': str(req.path),
        'request_full_path': str(req.full_path),
        'request_script_root': str(req.script_root),
        'request_url': str(req.url),
        'request_base_url': str(req.base_url),
        'request_url_root': str(req.url_root),
        'request_args': str(json.dumps(req.args, default=str)),
        'request_authorization': str(req.authorization),
        'request_content_type': str(req.content_type),
        'request_cookies': str(req.cookies),
        'request_data': str(req.data),
        'request_endpoint': str(req.endpoint),
        'request_form': str(req.form),
        'request_get_data': str(req.get_data()),
        'request_get_json': str(req.get_json()),
        'request_host': str(req.host),
        'request_host_url': str(req.host_url),
        'request_is_secure': str(req.is_secure),
        'request_json': str(req.json),
        'request_method': str(req.method),
        'request_query_string': str(req.query_string),
        'request_referrer': str(req.referrer),
        'request_remote_addr': str(req.remote_addr),
        'request_remote_user': str(req.remote_user),
        'request_scheme': str(req.scheme),
        'request_url_rule': str(req.url_rule),
        'request_user_agent': str(req.user_agent),
        'request_view_args': str(req.view_args)
    })

@app.route('/examples', methods=['GET', 'PUT', 'POST', 'DELETE'])
def get_examples():
    #show_request(request)
    return jsonify({
        'HOSTNAME': os.environ['HOSTNAME'],
        'HOME': os.environ['HOME'],
        'MESSAGE': 'get_examples',
        'request_path': str(request.path),
        'request_full_path': str(request.full_path),
        'request_script_root': str(request.script_root),
        'request_url': str(request.url),
        'request_base_url': str(request.base_url),
        'request_url_root': str(request.url_root),
        'request_method': str(request.method),
        'request_data': str(request.data),
        'request_query_string': str(request.query_string)
    })
    #return get_jsonify_request(request)

@app.route('/examples/<int:id>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def get_examples_id(id):
    print(id)
    #show_request(request)
    #return get_jsonify_request(request)
    return jsonify({
        'HOSTNAME': os.environ['HOSTNAME'],
        'HOME': os.environ['HOME'],
        'MESSAGE': 'get_examples',
        'request_path': str(request.path),
        'request_full_path': str(request.full_path),
        'request_script_root': str(request.script_root),
        'request_url': str(request.url),
        'request_base_url': str(request.base_url),
        'request_url_root': str(request.url_root),
        'request_method': str(request.method),
        'request_data': str(request.data),
        'request_query_string': str(request.query_string)
    })

if __name__ == '__main__':
    #app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(debug=True,host='0.0.0.0')
