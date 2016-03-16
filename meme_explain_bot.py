__author__ = 'Jonarzz'

"""Just a sketch (working)!"""
# TODO: reddit connection (PRAW)
# TODO: get comments starting with defined phrase from API Endpoint
# TODO: adding comments based of the outcome of database selects
# TODO: create a database with already done comments; use it

import sqlite3


conn = sqlite3.connect('meme.db')
c = conn.cursor()

# c.execute("SELECT links FROM memes WHERE meme='aaa'")
# print('nie: ', c.fetchone())

query = "james s"

c.execute("SELECT links FROM memes WHERE meme LIKE ?", ['%' + query + '%'])
results = list(set(c.fetchall()))
if len(results) == 1:
    print('One result1: ', results[0][0])
elif len(results) > 1:
    for result in results:
        print('More than one result1: ', result[0])
else:
    links = {}
    for word in query.split(' '):
        c.execute("SELECT links FROM memes WHERE meme LIKE ?", ['%' + word + '%'])
        for result in c.fetchall():
            if result[0] in links:
                links[result[0]] += 1
            else:
                links[result[0]] = 1

    results = [k for k,v in links.items() if v == max(links.values())]
    if len(results) == 1:
        print('One result2: ', results[0])
    else:
        for result in results:
            print('More than one result2: ', result)

conn.close()