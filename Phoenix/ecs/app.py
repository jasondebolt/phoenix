from flask import Flask
from flask import jsonify
import os
import copy

app = Flask(__name__)

@app.route('/')
def hello_world():
    my_dict = copy.deepcopy(os.environ)
    my_dict['Hello'] = 'Blah'
    return jsonify(my_dict)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
