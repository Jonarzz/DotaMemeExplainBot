__author__ = 'Jonarzz'

"""Main module of the bot responsible for looking up the query in the database and posting replies
to the comment in which the bot was called.
Also contains methods to perform operations on comments database."""
# TODO: reddit connection (PRAW) - reddit_account module


import sqlite3
from datetime import datetime
import time
from urllib.request import urlopen
import re

import praw

import reddit_account as account


def main():
    log('START')

    try:
        reddit = account.get_account()

        request = urlopen('https://api.pushshift.io/reddit/search?q="ExplainTheMeme"&limit=100&subreddit=dota2')
        json = request.json()
        comments = json["data"]
        for comment in comments:
            if already_checked(comment.id):
                continue

            add_to_already_checked(comment.id)

            original_comment = praw.objects.Comment(reddit, comment)

            match = re.match('ExplainTheMeme:?(.*)', comment.body)
            if not match:
                original_comment.reply('Your request seems to be invalid. Read the instructions on GitHub and try again or contact the bot administrator.')
            else:
                original_comment.reply(create_reply(match.group(1).strip()))

        time.sleep(30)
    except Exception as e:
        print(e)
        time.sleep(30)


def already_checked(comment_id):
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()

    c.execute("SELECT id FROM comments WHERE id=?", [comment_id])

    try:
        if c.fetchone():
            return True
        return False
    finally:
        conn.close()


def add_to_already_checked(comment_id):
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()

    c.execute("INSERT INTO comments VALUES (?)", [comment_id])

    conn.commit()
    conn.close()


def create_reply(query):
    conn = sqlite3.connect('meme.db')
    c = conn.cursor()

    c.execute("SELECT links FROM memes WHERE meme LIKE ?", ['%' + query + '%'])
    results = list(set(c.fetchall()))
    if len(results) == 1:
        reply = create_comment_for_one_result(query, results[0][0])
    elif len(results) > 1:
        reply = create_comment_for_multiple_results(query, results)
    else:
        links = {}
        for word in query.split(' '):
            c.execute("SELECT links FROM memes WHERE meme LIKE ?", ['%' + word + '%'])
            for result in c.fetchall():
                if result[0] in links:
                    links[result[0]] += 1
                else:
                    links[result[0]] = 1

        results = [k for k, v in links.items() if v == max(links.values())]
        if len(results) == 1:
            reply = create_comment_for_one_result(query, results[0])
        elif len(results) > 1:
            reply = create_comment_for_multiple_results(query, results)
        else:
            reply = 'No results were found in the Dota 2 Meme Database for your query: ' + query + '\nYou might want to check out [the original thread with meme list](https://www.reddit.com/r/DotA2/comments/4an9xd/a_trip_down_memery_lane_now_with_links_2nd_edition/).'

    conn.close()

    return reply


def create_comment_for_one_result(query, result):
    links = result.split(' | ')

    if len(links) == 1:
        return 'You asked about: ' + query + '\nThis [link](' + links[0] + ') may help you understand the meme!'

    comment = 'You asked about: ' + query + '\nThese links: '
    for link in links:
        comment += '[link](' + link + ') '
    comment += 'may help you understand the meme!'

    return comment


def create_comment_for_multiple_results(query, results):
    comment = 'You asked about: ' + query + '\nIt may be related to different memes. Check the links below:\n'

    for result in results:
        links = result[0].split(' | ')
        for link in links:
            comment += '[link](' + link + ') '
        comment += '\n'

    return comment


def create_comments_database():
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS comments (id text)')
    conn.commit()
    c.close()


def log(message):
    print(str(datetime.now()) + ': ' + message + '\n')


if __name__ == '__main__':
    main()
