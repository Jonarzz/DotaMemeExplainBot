__author__ = 'Jonarzz'

"""Main module of the bot responsible for looking up the query in the database and posting replies
to the comment in which the bot was called.
Also contains methods to perform operations on comments database."""
# TODO: adding memes by users


import sqlite3
from datetime import datetime
import time
from urllib.request import urlopen
import re
import traceback
import json

import properties
import reddit_account as account


def main():
    log('START')

    try:
        reddit = account.get_account()

        response = urlopen('https://api.pushshift.io/reddit/search?q="' + properties.BOT_CALL_PHRASE + \
                           '"&limit=100&subreddit=' + properties.SUBREDDIT)
        json_data = json.loads(response.read().decode('utf-8'))
        comments = json_data["data"]

        for comment in comments:
            if already_checked(comment['id']):
                continue

            if comment['author'] == 'dota_memes_bot':
                add_to_already_checked(comment['id'])
                continue

            submission_link = 'https://www.reddit.com' + comment['link_permalink'] + comment['id']
            submission = reddit.get_submission(submission_link)

            try:
                original_comment = submission.comments[0]
            except IndexError:
                add_to_already_checked(comment['id'])

            match = re.match(properties.BOT_CALL_PHRASE + ':?(.*)', comment['body'])

            if not match or match.group(1).strip() == '':
                reply_to_comment(original_comment, comment['id'], properties.INVALID_REQUEST_REPLY)
            else:
                query = match.group(1).strip()
                if len(query) > 2 and len(query) < 150:
                    reply_to_comment(original_comment, comment['id'], create_reply(query))
                else:
                    reply_to_comment(original_comment, comment['id'], properties.INVALID_COMMENT_LENGTH_REPLY)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        log(traceback.format_exc())
    finally:
        time.sleep(30)


def reply_to_comment(original_comment_object, original_comment_id, reply):
    try:
        original_comment_object.reply(reply)
    except:
        raise

    add_to_already_checked(original_comment_id)
    log(original_comment_id)


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
    original_query = query
    query = query.strip().strip('.').strip('!').lower()

    conn = sqlite3.connect('meme.db')
    c = conn.cursor()

    c.execute("SELECT links FROM memes WHERE meme LIKE ?", ['%' + query + '%'])
    results = list(set(c.fetchall()))
    if len(results) == 1:
        reply = create_comment_for_one_result(original_query, query, results[0][0])
    elif len(results) > 1:
        reply = create_comment_for_multiple_results(original_query, query, results)
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
            reply = create_comment_for_one_result(original_query, query, results[0])
        elif len(results) > 1:
            reply = create_comment_for_multiple_results(original_query, query, results)
        else:
            reply = 'No results were found in the Dota 2 Meme Database for your query: ' + original_query + \
                    '\n\nYou might want to check out [the original thread with the meme list]' + \
                    '(https://www.reddit.com/r/DotA2/comments/4an9xd/a_trip_down_memery_lane_now_with_links_2nd_edition/).' + \
                    properties.COMMENT_ENDING

    conn.close()

    return reply


def create_comment_for_one_result(original_query, query, result):
    links = result.split(' | ')

    if len(links) == 1:
        return 'You asked about: ' + original_query + '\n\nThis [link](' + links[0] + ') may help you understand the meme!' + \
               properties.COMMENT_ENDING

    comment = 'You asked about: ' + original_query + '\n\nThese links: '
    for link in links:
        comment += '[link](' + link + ') '
    comment += 'may help you understand the meme!'

    comment += properties.COMMENT_ENDING

    return comment


def create_comment_for_multiple_results(original_query, query, results):
    i = 1

    comment = 'You asked about: ' + original_query + '\n\nIt may be related to different memes. Check the links below:\n\n'

    for result in results:
        comment += str(i) + ': '
        i += 1

        links = result[0].split(' | ')
        for link in links:
            comment += '[link](' + link + ') '
        comment += '\n\n'

    if len(comment.splitlines()) > 13:
        comment = properties.TOO_MANY_RESULTS_REPLY

    comment += properties.COMMENT_ENDING[2:]

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
    while True:
        main()
