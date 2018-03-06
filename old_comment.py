"""
AvgComment_bot. A Reddit bot that can be summoned and used to
calculated the Averages of comments. Currently supports the use 
of the Flesch-Kincaid model to find the average grade level
a comment was written at. Hoping to add:

1. Average sentence, which aggregates total words in a thread and 
   attempts to make a sentence out of it.
2. Switch to check downvoted comments versus upvoted comments 
   and compare the average reading level between them.


"""

__author__ = "/u/happyness_"

import praw
from curses.ascii import isdigit
from nltk.corpus import cmudict
import string
from string import digits
import sqlite3
import datetime
import time


def reddit_login():
    """
    Initialize our connection to Reddit. Uses OAuth as a Script Application
    
    :return: 
    """
    try:
        bot_init = praw.Reddit(client_id='XXXXXXXXXXXXXX',
                             client_secret='XXXXXXXXXXXXXXXXXXXX',
                             password='XXXXXXXXXXXXXXXXXXXXXX',
                             user_agent='HappyBot v 0.1 by /u/happyness_',
                             username='happyness_bot')
        return bot_init
    except Exception as e:
        print(e)


def insert_body(r):
    conn = sqlite3.connect("comment.db")
    c = conn.cursor()
    c.execute("SELECT CommentID FROM comments WHERE body IS NULL")
    rows = c.fetchall()
    result = [x[0] for x in rows]
    for cid in result:
        try:
            #print(cid)
            comment_body = r.comment("{}".format(cid)).body
            safe_comment = comment_body.replace("'", "''")
            with conn:
                c.execute("UPDATE comments SET body = '{}' WHERE CommentID = '{}'".format(safe_comment, cid))
                #print("\nComment " + cid + " updated successfully. Body: \n\n" + safe_comment)
                print("Comment " + cid + " updated.")
            time.sleep(1)
        except Exception as e:
            print(e)


r = reddit_login()
insert_body(r)
