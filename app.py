from flask import Flask, request, jsonify, make_response,json
from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT, jwt_required, current_identity
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from APIs.model.connectionString import db
import APIs.model.connectionString
from APIs.model.dbconnect import User,Clientinfo

app = Flask(__name__)

# app = Flask("__name__")
app.config['SECRET_KEY'] = '\x17H\xb4\x1d\xa4\xa59VC\xc7\xe2d;O\xb1\xb9\xb4\x04\xdeM#\x8d\x9e\x03'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://clementbatie:deworma@localhost:5432/discover_flask_dev'
db = SQLAlchemy(app)

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):

		token = request.args.get('token')

		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({'' : ' '}), 401

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
			curent_user = User.query.filter_by(public_id=data['public_id']).first()
		except:
			return jsonify({'' : ' '}), 401

		return f(curent_user, *args, **kwargs)

	return decorated

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function'})

	users = User.query.all()

	output = []

	for user in users:
		user_data = {}
		user_data['public_id'] = user.public_id
		user_data['name'] = user.name
		user_data['password'] = user.password
		user_data['admin'] = user.admin
		output.append(user_data)

	return jsonify({'users' : output})

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_single_user(current_user, public_id):

	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function'})

	user = User.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message' : 'No user found!'})

	user_data = {}
	user_data['public_id'] = user.public_id
	user_data['name'] = user.name
	user_data['password'] = user.password
	user_data['admin'] = user.admin

	return jsonify({'user' : user_data})

@app.route('/user', methods=['POST'])
@token_required
def create_users(current_user):
	auth = request.data
	info = json.loads(auth)
	username = info['username']
	password = info['password']

	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function'})

	data = request.get_json()

	hashed_password = generate_password_hash(info['password'], method='sha256')

	new_user = User(public_id=str(uuid.uuid4()), name=info['username'], password=hashed_password, admin=False)
	db.session.add(new_user)
	db.session.commit()

	return jsonify({'message' : 'New user created!'})

@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def changeuserstatus(current_user, public_id):

	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function'})

	user = User.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message' : 'No user found!'})

	user.admin = True
	db.session.commit()

	return jsonify({'message' : 'User has been promoted'})

@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):

	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function'})

	user = User.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message' : 'No user found!'})

	db.session.delete(user)
	db.session.commit()

	return jsonify({'message' : 'The user has been deleted'})

@app.route('/login', methods=['POST'])
def login():
	auth = request.data
	info = json.loads(auth)
	username = info['username']
	password = info['password']
	# return tt

	if not auth or not username or not password:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

	user = User.query.filter_by(name=username).first()

	if not user:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

	if check_password_hash(user.password, password):
		token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=30)}, app.config['SECRET_KEY'])

		return jsonify({'token' : token.decode('UTF-8'),'username':username, 'admin':user.admin})

	return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

@app.route('/allclients', methods=['GET'])
@token_required
def get_all_clients(current_user):

	todos = Clientinfo.query.all()

	output = []

	for todo in todos:
		todo_data = {}
		todo_data['id'] = todo.id
		todo_data['clientname'] = todo.clientname
		todo_data['accountnumber'] = todo.accountnumber
		todo_data['amount'] = str(todo.amount)
		todo_data['numberoftran'] = todo.numberoftran
		todo_data['gender'] = todo.gender
		output.append(todo_data)

	return jsonify({'clients' : output})


@app.route('/clientinfo', methods=['POST'])
@token_required
def create_todo(current_user):
	data = request.get_json()

	new_todo = Clientinfo(clientname=data['name'],accountnumber=data['number'],amount=data['amount'],numoftran=data['transaction'], gender=data['gender'], userid=current_user.id)
	db.session.add(new_todo)
	db.session.commit()
	return jsonify({'message' : 'Client Information Created!'})




if __name__ == '__main__':
	app.run(debug=True)
