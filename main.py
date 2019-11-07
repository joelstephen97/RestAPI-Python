import requests
import sqlite3


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




