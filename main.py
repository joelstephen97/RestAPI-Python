import requests
import sqlite3
from ratelimit import limits,sleep_and_retry,RateLimitException
from backoff import on_exception,expo

'''
System Necessary Variables
'''
FIVE_MINUTES = 300

connection = sqlite3.connect('database.db') #connect to database
cursor = connection.cursor() #instantiate the cursor object


'''
Definitions
'''
@sleep_and_retry
@on_exception(expo, RateLimitException, max_tries=300)
@limits(calls=300, period=FIVE_MINUTES)
def call_api():
    '''
    Rules for 300 requests in 5 mins has been implemented using the ratelimit module.
    This function will call the ReST API and read the data.
    If the

    :return: data which is a JSON object.
    '''
    url = 'https://jsonplaceholder.typicode.com/comments'
    resp = requests.get(url=url)
    data = resp.json()

    if resp.status_code != 200:
        raise Exception('API response: {}'.format(resp.status_code))
    return data



def drop_table():
    '''
    If table exists, Drop table.

    :return:
    '''
    cursor.execute ("DROP TABLE IF EXISTS data_table")
    connection.commit()

def create_table():
    '''
    If table does not exist, Table is create.
    If exists, return error.
    Error is caught in try/except loop.
    :return:
    '''
    sql_command = """
        CREATE TABLE IF NOT EXISTS data_table (
                            postId INTEGER,
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(1000),
                            email VARCHAR(200),
                            body CHAR(1000));"""



    try:
        cursor.execute(sql_command)
        connection.commit()
    except:
        pass


