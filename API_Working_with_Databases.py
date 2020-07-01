from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Float, String
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required,create_access_token
from flask_mail import Mail,Message

##Working with SQLlite Serverless database
##Using ORM (Object Relational Mapper) we can use python objects to retrieve data from databases

database = Flask(__name__)  #constructor

##As a file base database system, we need to tell the application where to store the file
basedir = os.path.abspath(os.path.dirname(__file__)) ## putting database file in the same application as running folder
database.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db') ## adding configuration variables using congiguration manager
database.config['JWT_SECRET_KEY'] = 'super-secret'
## Setting up Flask Mail
database.config['MAIL_SERVER']='smtp.mailtrap.io'
database.config['MAIL_PORT'] = 2525
database.config['MAIL_USERNAME'] = 'd0190d7f52cac6'
database.config['MAIL_PASSWORD'] = 'd956774dbf644b'
database.config['MAIL_USE_TLS'] = True
database.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(database) # Initializing the database
ma = Marshmallow(database)
jwt = JWTManager(database)
mail = Mail(database)

@database.cli.command('db_create') # Decorator
def db_create():
    db.create_all() # Coming from SQLAlchemy
    print('Database Created.')

@database.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped.')

@database.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',
                     planet_type='Class D',
                     home_star='Sol',
                     mass = 3.258e23,
                     radius=1516,
                     distance=35.89e6)

    venus = Planet(planet_name='Venus',
                     planet_type='Class K',
                     home_star='Sol',
                     mass = 4.867e24,
                     radius=3760,
                     distance=67.24e6)

    earth = Planet(planet_name='Earth',
                     planet_type='Class M',
                     home_star='Sol',
                     mass = 5.972e24,
                     radius=3959,
                     distance=92.96e6)

    db.session.add(mercury)
    db.session.add(mercury)
    db.session.add(mercury)

    test_user = User(first_name='William',
                     last_name='Herschel',
                     email='test@test.com',
                     password='P@ssw0rd')

    db.session.add(test_user)
    db.session.commit()
    print('Database seeded')


@database.route('/planets',methods=['GET'])
def planets():
    planets_list = Planet.query.all() # get all data from Planets table in the database using SQLAlchemy
    result = planets_schema.dump(planets_list) # getting all data present in planets table in the database
    return jsonify(result)

@database.route('/register',methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first() # to check if email already exist in the database
    if test:
        return jsonify(message='That email already exists.'), 409
    else:
        first_name = request.form['first_name'] # taking the first name from the form filled
        last_name = request.form['last_name'] # taking the last name from the form filled
        password = request.form['password'] # taking the password from the form filled
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User created successfully.'), 201


@database.route('/login',methods=['POST'])
def login():
    ## using JSON instead of form fields
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email,password=password).first() # to check if email already exist in the database
    if test:
        access_token = create_access_token(identity=email) # identifying the user for authentication
        return jsonify(message='Login Succeeded',access_token=access_token)
    else:
        return jsonify(message='Bad Email or Password'), 401


@database.route('/retrieve_password/<string:email>',methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg=Message('Your planetary API password is ' + user.password,
                    sender='admin@planetary-api.com',
                    recipients=['email'])
        mail.send(msg)
        return jsonify(message='Password sent to ' + email)
    else:
        return jsonify(message='That email does not exist'), 401


# retrieve a single planet's detail
@database.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message='That planet does not exist'), 404


## Adding a planet to the database using POST method
@database.route('/add_planet',methods=['POST'])
@jwt_required #Securing the add planet endpoint using JWT token'
def add_planet():
    planet_name = request.form['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify('Planet already exist'), 409
    else:
        planet_type = request.form['planet_type']
        home_star = request.form['home_star']
        mass = request.form['mass']
        radius = request.form['radius']
        distance = request.form['distance']

        new_planet = Planet(planet_name=planet_name,
                            planet_type=planet_type,
                            home_star=home_star,
                            mass=mass,
                            radius=radius,
                            distance=distance)
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message='You added a planet'), 201


## Updating the planet
@database.route('/update_planet',methods=['PUT'])
@jwt_required
def update_planet():
    planet_id = int(request.form['planet_id'])
    test = Planet.query.filter_by(planet_id=planet_id).first()
    if test:
        test.planet_name = request.form['planet_name']
        test.planet_type = request.form['planet_type']
        test.home_star = request.form['home_star']
        test.mass = float(request.form['mass'])
        test.radius = float(request.form['radius'])
        test.distance = float(request.form['distance'])
        db.session.commit()
        return jsonify(message='You updated a planet'), 202
    else:
        return jsonify(message='That planet does not exist'), 404


## Removing a planet from the database
@database.route('/remove_planet/<int:planet_id>', methods=['DELETE'])
@jwt_required
def remove_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message='You deleted a planet'), 201
    else:
        return jsonify(message='no planet'), 404


## Creating a User table in Database ## library db.model to use this class'
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

## Creating a Planet table in Database
class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer,primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

# werkzeug is a python web services gateway interface, responsible for serving up our data in response to the endpoint definitions
# we have made in flask
# Serializing SQLAlchemy results with Marshmallow
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','first_name','last_name','email','password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id','planet_name','planet_type','home_star','mass','radius','distance')


user_schema = UserSchema() #deserializing the single object
users_schema = UserSchema(many=True) #deserializing many objects

planet_schema = PlanetSchema(many=False)
planets_schema = PlanetSchema(many=True)

## List detail/master detail patter
## Using endpoint URL we will display all the records from the database
if __name__ == '__main__':
    database.run()