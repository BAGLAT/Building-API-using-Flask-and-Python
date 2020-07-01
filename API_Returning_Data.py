from flask import Flask, jsonify, request

new = Flask(__name__)


@new.route('/')
def hello_world_new():
    return jsonify(message='Hello World')


@new.route('/simple')
def hello_world():
    return jsonify(message='Super Hello World')


@new.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found'), 404


@new.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message='Hello ' + name + ', you are not old enough'), 401
    else:
        return jsonify(message='Welcome ' + name + ', you are old enough')


@new.route('/url_variable/<string:name>/<int:age>')
def url_variable(name: str, age: int):
    if age < 18:
        return jsonify(message='Sorry ' + name + ', you are not old enough'), 401
    else:
        return jsonify(message='Welcome ' + name + ', you are old enough')


if __name__ == '__main__':
    new.run()