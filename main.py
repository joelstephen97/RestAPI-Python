import requests
import sqlite3
from ratelimit import limits, sleep_and_retry, RateLimitException
from backoff import on_exception, expo


'''
System Necessary Variables
'''
FIVE_MINUTES = 300

connection = sqlite3.connect('database.db')  # connect to database
cursor = connection.cursor()  # instantiate the cursor object


'''
Definitions
'''


@sleep_and_retry
@on_exception(expo, RateLimitException, max_tries=300)
@limits(calls=300, period=FIVE_MINUTES)
def call_api():
    """
    Rules for 300 requests in 5 mins has been implemented using the ratelimit module.
    This function will call the ReST API and read the data.
    If the

    :return: data which is a JSON object.
    """
    url = 'https://jsonplaceholder.typicode.com/comments'
    resp = requests.get(url=url)
    data = resp.json()

    if resp.status_code != 200:
        raise Exception('API response: {}'.format(resp.status_code))
    return data


def drop_table():
    """
    If table exists, Drop table.

    :return:
    """
    cursor.execute("DROP TABLE IF EXISTS data_table")
    connection.commit()


def create_table():
    """
    If table does not exist, Table is create.
    If exists, return error.
    Error is caught in try/except loop.
    :return:
    """
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


def write_data_to_table():
    """
    Instruction passed to create table.
    call_api() function is called and data variable accepts data.JSON object.

    for loop loops through the JSON and inserts all data into the table.

    When all data has been entered a message is flashed to show the number of data points inserted to table.
    :return:
    """
    create_table()
    data = call_api()

    for i in data:
        a = i['body'].replace('\n', ' ')
        format_str = """INSERT INTO data_table
                        (
                            postId,
                            id,
                            name,
                            email,
                            body                   
    
                        ) 
                        VALUES ({postId}, {id}, "{name}", "{email}", "{body}");"""
        sql_command = format_str.format(postId=i['postId'], id=i['id'], name=i['name'], email=i['email'], body=a)
        cursor.execute(sql_command)
        if i['id'] == len(data):
            print(f"{i['id']} data fields have been entered into table from the ReST API.")
        else:
            pass
    connection.commit()


def runnable():
    """
    This definition is to provide a concise running enviroment to enhance usability only.
    functions are called per user instructions making the user experience optimal.
    :return:
    """
    print('Hello, Welcome to the Database. ')
    print('''
    Your options are :
    1. Write DATA from https://jsonplaceholder.typicode.com/comments
    2. Delete Existing Data from Table 
    3. Exit''')

    def options():
        option_input = int(input("Enter Option: "))
        if option_input == 1:
            try:
                write_data_to_table()
                print('\n')
                options()
            except:
                print('''Oops, Looks like data already exists. Enter option 2 and try again. ''')
                print('\n')
                options()
        elif option_input == 2:
            drop_table()
            print('Existing table has been dropped successfully!')
            create_table()
            print('Created new table to store your data.')
            print('\n')
            options()
        elif option_input == 3:
            print('Thank you for using the Program. Exiting Now.')

        else:
            print('Invalid Option Choice, please enter the valid choice again.')
            print('\n')
            options()

    options()


runnable()
