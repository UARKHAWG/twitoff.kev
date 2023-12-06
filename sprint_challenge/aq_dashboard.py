'''
OpenAQ Air Quality Dashboard with Flask.
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB = SQLAlchemy(app)

# API obj
api = openaq.OpenAQ()


def get_data(city, parameter):
    '''
    retrieve data by city and param
    '''
    api = openaq.OpenAQ()
    status, body = api.measurements(city=city, parameter=parameter)
    results = [
        (result['date']['utc'], result['value'])
        for result in body['results']
        ]
    return results


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
        city='Los Angeles', parameter='pm25'
    )
    results = body['results']
    values = []
    for result in results:
        values.append((result['date']['utc'], result['value']))
    return values


@app.route('/')
def root():
    '''
    Main route
    '''
    roots = query_DB()
    return roots


@app.route('/refresh')
def refresh():
    '''
    Pull fresh data from Open AQ and replace existing data.
    '''

    DB.drop_all()
    DB.create_all()

    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    for result in get_data('Los Angeles', 'pm25'):
        record = Record(datetime=str(result[0]), value=result[1])
        DB.session.add(record)
    DB.session.commit()
    return'Data Refreshed'


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
    id = DB.Column(DB.Integer, primary_key=True)
    # datetime (string)
    datetime = DB.Column(DB.String(25))
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'< -- Date & Time {self.datetime} --- Value {self.value} -- >'
