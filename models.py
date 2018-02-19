import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('learning_journal.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password),
                    is_admin = admin
                )
        except IntegrityError:
            raise ValueError("User already exists!")


class Entry(Model):
    title = CharField(unique=True)
    created_date = DateTimeField(default=datetime.datetime.now)
    date = DateTimeField()
    time_spent = IntegerField()
    learned = TextField()
    resources = TextField()
    deleted = BooleanField(default=False)
    tags = TextField()
    user = ForeignKeyField(User)

    class Meta:
        database = DATABASE

    @classmethod
    def create_entry(cls, title, date, time_spent, learned, resources, deleted, tags, user):
        try:
            with DATABASE.transaction():
                cls.create(
                    title=title,
                    date=date,
                    time_spent=time_spent,
                    learned=learned,
                    resources=resources,
                    deleted=deleted,
                    tags=tags,
                    user=user
                )
        except IntegrityError:
            raise ValueError("This title already exists!")


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry], safe=True)
    DATABASE.close()
