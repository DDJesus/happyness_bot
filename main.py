"""

This is just a automated version of avgcomment_bot. It is just set up to 
analyze all comments coming in from /r/all, across all SubReddits. It doesn't 
make any replies, doesn't wait for any keywords, it just takes in all comments
and determines their Flesch-Kincaid readability level. This is so we can
start getting data without having to wait for avgcomment_bot to be
summoned.

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
    bot_init = praw.Reddit(client_id='XXXXXXXXXXX',
                         client_secret='XXXXXXXXXXXXXXXX',
                         password='XXXXXXXXXXXXXXXX',
                         user_agent='HappyBot v 0.1 by /u/happyness_',
                         username='happyness_bot')
    return bot_init


def comment_reader(r):
    """
    Reads comments from /r/all with a 1 second delay.

    :param r: reddit login function
    :return: 
    """
    conn = sqlite3.connect("comment.db")
    c = conn.cursor()
    for comment in r.subreddit("all").stream.comments():

        try:
            c.execute("SELECT CommentID FROM comments WHERE CommentID = '{0}'".format(comment.id))
            if c.fetchone():  # If our query above returns a result then pass
                pass
            else:
                print("Found comment " + comment.id + " to analyze.")
                print("Analyzing comment...")
                comment_date = datetime.datetime.fromtimestamp(comment.created)
                f_kinc = comment_analyzer(comment.body)  # Get comments Flesch-Kincaid results
                print("Inserting known values in to Database: comment")
                if f_kinc < 0:
                    pass
                else:
                    with conn:
                        c.execute("INSERT INTO comments values('{0}', {1}, '{2}', '{3}')".format(comment.id,
                                                                                                 f_kinc,
                                                                                                 comment_date,
                                                                                                 comment.subreddit))
                    print("Comment ID {} had a Flesch Kincaid result of {}".format(comment.id, f_kinc))
                time.sleep(1)
        except (AttributeError, TypeError) as e:  # Sometimes the f_kinc function returns NoneType. Idk why, but we catch it.
            continue


def comment_analyzer(comment_body):
    """
    Function that analyzes comment bodies to determine the Flesh-Kincaid
    reading level of the comment.
    We need to:

        1. Calculate the average number of words used per sentence
        2. Calculate the average number of syllables per word
        3. Multiply the average number of words by 0.39 and add it
           to the average number of syllables per word multiplied by
           11.8
        4. Subtract 15.59 from the result.

    :param comment_body: string
    :return: 
    """
    syllable_count = 0
    word_count = 0
    sentence_count = 0

    for word in comment_body.split():
        try:
            remove_digits = str.maketrans('', '', digits)
            word = word.translate(remove_digits)  # Removes digits 1-9 from being checked
            # Once digits are stripped, they show up as ''.
            # This next line just says to ignore them if that's the case
            if word == '':
                continue
            endings_repeat = ["..", "??", "!!"]
            if any(i in word for i in endings_repeat):
                sentence_count += 1
            else:
                sentence_count += word.count(".")
                sentence_count += word.count("?")
                sentence_count += word.count("!")

            word_count += 1
            translator = str.maketrans('', '', string.punctuation)
            word = word.translate(translator)  # Removes punctuation from word
            syllable_list = nsyl(word)  # Flesh-Kincaid bit ( see nsyl() )
            syllable_count += syllable_list[0]
        except KeyError:
            pass

    if sentence_count == 0:
        sentence_count = 1
    try:
        print("Sentences: " + str(sentence_count))
        average_words = word_count / sentence_count  # Average words used per sentence
        print("Avg words: " + str(average_words))
        average_syllables = syllable_count / word_count  # Average syllables per word
        print("Avg syllables: " + str(average_syllables))
        # All our step three stuff. ( See function details for more information )
        step_three_words = (average_words * .39)
        step_three_syllables = (average_syllables * 11.8)
        step_three_added = (step_three_words + step_three_syllables)
        # Find our final result, the round to the nearest integer.
        result = (step_three_added - 15.59)
        return int(round(result))
    except ZeroDivisionError as e:
        print("Comment contained zero words. Continuing.")
        pass


d = cmudict.dict()


def nsyl(word):
    """
    The actual magic. Takes a word and makes use to the Natural Language Tool-Kit (nltk) 
    to count the syllables for the word. 
    DEPENDS ON A PRE-DETERMINED DICTIONARY OF ENGLISH LANGUAGE WORDS. IF THE WORD DOES NOT
    MATCH WORD ON THE LIST, THE WORD IS EXCLUDED FROM THE FINAL RESULTS.

    :param word: string
    :return: 
    """
    return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]


r = reddit_login()
comment_reader(r)

# Use the below to check outlier comments (48 grade level for the word "Communism?" LOL)
# print(r.comment("dih6m0a").body)
