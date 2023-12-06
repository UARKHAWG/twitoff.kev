'''
OpenAQ Air Quality Dashboard with Flask.
'''
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq
import random

app = Flask(__name__)

# API obj
api = openaq.OpenAQ()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB = SQLAlchemy(app)


@app.route('/')
def root():
    '''
    Main route
    '''
    roots = query_DB()
    return roots


def query_DB():
    '''
    query DB to check results
    '''
    condition = Record.query.filter(Record.value >= 18).all()

    return str(condition)


def get_results():
    '''
    get results with certain params
    '''
    api = openaq.OpenAQ()
    status, body = api.measurements(
        city='Los Angeles', parameter='pm25', limit=100
        )
    utc = []
    values = []
    for result in body['results']:
        utc.append(result["date"]["utc"])
        values.append(result["value"])
    res = list(zip(utc, values))
    return res


@app.route('/refresh')
def refresh():
    '''
    Pull fresh data from Open AQ and replace existing data.
    '''

    DB.drop_all()
    DB.create_all()

    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    refreshed = get_results()
    for result in refreshed:
        add_record = Record(result[0], result[1])
        DB.session.add(add_record)
        DB.session.commit()
    # Retrieve all records from the database
    records = Record.query.all()
    return str(records)


@app.route('/reset')
def reset():
    '''
    reset DB to ensure nothing is in DB before refreshing
    '''
    DB.drop_all()
    DB.create_all()
    return'DB reset!!!'


class Record(DB.Model):
    '''
    Create class with 3 attributes
    , id
    , datetime(string since sql doesnt recognize datetime objects)
    , and value(float)
    '''

    # id (integer, primary key)
    id = DB.Column(DB.Integer, primary_key=True, nullable=False)
    # datetime (string)
    datetime = DB.Column(DB.String)
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __init__(self, datetime, value):
        self.id = random.randint(0, 1000000000)
        self.datetime = str(datetime)
        self.value = value

    def __repr__(self):
        return f" -- Date:{self.datetime} -- Value: {self.value} -- "

    
def test_refresh_route():
    """
    Testing app.route('refresh/') - Test the string output we get from
    refresh.
    """


    refreshed_string = refresh()
    records = Record.query.all()

    refreshed_string2 = refresh()
    records_tester = Record.query.all()

    assert "refreshed" in refreshed_string.lower()
    #assert 'refreshed' in "[ -- date:'2016-01-30t02:00:00+00:00' -- value: 46.13 -- ,  -- date:'2016-02-01t06:00:00+00:00' -- value: 18.66 -- , ... ,  -- date:'2016-01-30t06:00:00+00:00' -- value: 45.45 -- ,  -- date:'2016-02-02t22:00:00+00:00' -- value: 71.23 -- ]" + "[ -- date:'2016-01-30t02:00:00+00:00' -- value: 46.13 -- ,  -- date:'2016-02-01t06:00:00+00:00' -- value: 18.66 -- , ... ,  -- date:'2016-01-30t06:00:00+00:00' -- value: 45.45 -- ,  -- date:'2016-02-02t22:00:00+00:00' -- value: 71.23 -- ]" = <built-in method lower of str object at 0x2242b20>() +    where <built-in method lower of str object at 0x2242b20> = "[ -- Date:'2016-01-30T02:00:00+00:00' -- Value: 46.13 -- ,  -- Date:'2016-02-01T06:00:00+00:00' -- Value: 18.66 -- , ... ,  -- Date:'2016-01-30T06:00:00+00:00' -- Value: 45.45 -- ,  -- Date:'2016-02-02T22:00:00+00:00' -- Value: 71.23 -- ]".lower
