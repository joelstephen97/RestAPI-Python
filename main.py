"""Fetch comments from the JSONPlaceholder REST API and store them in SQLite.

Written in November 2019 as a take-home "full stack developer test". The brief was:
call a public REST API, respect a rate limit of 300 requests per 5 minutes, and
persist the JSON into a database table.

Usage:
    python main.py            interactive menu (the original behaviour)
    python main.py fetch      download comments and insert them
    python main.py reset      drop and recreate the table
    python main.py show [-n]  print the first n rows
    python main.py count      number of stored rows
"""

import argparse
import os
import sqlite3
import sys

import requests
from backoff import expo, on_exception
from ratelimit import RateLimitException, limits, sleep_and_retry

API_URL = "https://jsonplaceholder.typicode.com/comments"
DB_PATH = os.getenv("DB_PATH", "database.db")
FIVE_MINUTES = 300

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


@sleep_and_retry
@on_exception(expo, RateLimitException, max_tries=300)
@limits(calls=300, period=FIVE_MINUTES)
def call_api():
    """GET the comments endpoint, limited to 300 calls per 5 minutes. Returns parsed JSON."""
    resp = requests.get(API_URL, timeout=30)
    if resp.status_code != 200:
        raise Exception("API response: {}".format(resp.status_code))
    return resp.json()


def drop_table():
    cursor.execute("DROP TABLE IF EXISTS data_table")
    connection.commit()


def create_table():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS data_table (
            postId INTEGER,
            id     INTEGER PRIMARY KEY,
            name   VARCHAR(1000),
            email  VARCHAR(200),
            body   CHAR(1000)
        );"""
    )
    connection.commit()


def write_data_to_table():
    """Create the table if needed, fetch the API, insert every comment. Returns rows inserted."""
    create_table()
    data = call_api()
    rows = [
        (item["postId"], item["id"], item["name"], item["email"], item["body"].replace("\n", " "))
        for item in data
    ]
    cursor.executemany(
        "INSERT INTO data_table (postId, id, name, email, body) VALUES (?, ?, ?, ?, ?)", rows
    )
    connection.commit()
    print(f"{len(rows)} data fields have been entered into table from the ReST API.")
    return len(rows)


def count_rows():
    create_table()
    return cursor.execute("SELECT COUNT(*) FROM data_table").fetchone()[0]


def show_rows(limit):
    create_table()
    for row in cursor.execute(
        "SELECT id, postId, email, substr(body, 1, 60) FROM data_table ORDER BY id LIMIT ?", (limit,)
    ):
        print("{:>4} post={:<3} {:<32} {}...".format(*row))


def runnable():
    """Interactive menu: the original 2019 user interface."""
    print("Hello, Welcome to the Database. ")
    print(
        """
    Your options are :
    1. Write DATA from https://jsonplaceholder.typicode.com/comments
    2. Delete Existing Data from Table
    3. Exit"""
    )
    while True:
        try:
            option_input = int(input("Enter Option: "))
        except ValueError:
            option_input = -1
        if option_input == 1:
            try:
                write_data_to_table()
            except sqlite3.IntegrityError:
                print("Oops, Looks like data already exists. Enter option 2 and try again. ")
            print()
        elif option_input == 2:
            drop_table()
            print("Existing table has been dropped successfully!")
            create_table()
            print("Created new table to store your data.\n")
        elif option_input == 3:
            print("Thank you for using the Program. Exiting Now.")
            return
        else:
            print("Invalid Option Choice, please enter the valid choice again.\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("menu", help="interactive menu (default)")
    sub.add_parser("fetch", help="download comments from the API and insert them")
    sub.add_parser("reset", help="drop and recreate the table")
    show = sub.add_parser("show", help="print stored rows")
    show.add_argument("-n", type=int, default=10, help="rows to print (default 10)")
    sub.add_parser("count", help="print the number of stored rows")
    args = parser.parse_args(argv)

    if args.cmd in (None, "menu"):
        runnable()
    elif args.cmd == "fetch":
        try:
            write_data_to_table()
        except sqlite3.IntegrityError:
            print("Data already exists in the table. Run `python main.py reset` first.", file=sys.stderr)
            return 1
    elif args.cmd == "reset":
        drop_table()
        create_table()
        print("Table dropped and recreated.")
    elif args.cmd == "show":
        show_rows(args.n)
    elif args.cmd == "count":
        print(count_rows())
    return 0


if __name__ == "__main__":
    sys.exit(main())
