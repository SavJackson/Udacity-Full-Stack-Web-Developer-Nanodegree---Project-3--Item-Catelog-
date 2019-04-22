from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database  # drop_database

database_file = 'postgresql://postgres:postgres@localhost/ItemCatalog'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
# silence the deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class AppUser(db.Model):
    __tablename__ = 'appuser'
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(25), index=False, unique=False)
    lastname = db.Column(db.String(25), index=True, unique=False)
    email = db.Column(db.String(100), index=True, unique=True)

    def __init__(self, userid, firstname, lastname, email):
        self.userid = userid
        self.firstname = firstname
        self.lastname = lastname
        self.email = email

    def __repr__(self):
        return '<User {}>'.format(self.firstname)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'userid': self.userid,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email
        }


class Category(db.Model):
    __tablename__ = 'category'
    categoryid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoryname = db.Column(db.String(50), index=True, unique=True)
    description = db.Column(db.String(120), index=False, unique=True)
    dateadded = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    userid = db.Column(db.Integer, index=True, unique=False)

    def __init__(self, categoryid, categoryname, description,
                 dateadded, userid):
        self.categoryid = categoryid
        self.categoryname = categoryname
        self.description = description
        self.dateadded = dateadded
        self.userid = userid

    def __repr__(self):
        return '<Category {}>'.format(self.categoryname)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'categoryid': self.categoryid,
            'categoryname': self.categoryname,
            'description': self.description,
            'dateadded': self.dateadded,
            'userid': self.userid
        }


class CategoryItem(db.Model):
    __tablename__ = 'categoryitems'
    itemid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    itemname = db.Column(db.String(50), index=True, unique=True)
    description = db.Column(db.String(120), index=False, unique=True)
    dateadded = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    categoryid = db.Column(db.Integer, index=True, unique=False)
    userid = db.Column(db.Integer, index=True, unique=False)

    def __init__(self, itemid, itemname, description, dateadded,
                 categoryid, userid):
        self.itemid = itemid
        self.itemname = itemname
        self.description = description
        self.dateadded = dateadded
        self.categoryid = categoryid
        self.userid = userid

    def __repr__(self):
        return 'CategoryItem {}>'.format(self.itemname)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
                'itemid': self.itemid,
                'itemname': self.itemname,
                'description': self.description,
                'dateadded': self.dateadded,
                'categoryid': self.categoryid,
                'userid': self.userid
        }


if not database_exists(database_file):
    print('Creating database.')
    create_database(database_file)

    print('Creating tables.')
    db.create_all()
