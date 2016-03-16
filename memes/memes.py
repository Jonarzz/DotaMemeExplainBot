# coding=UTF-8

__author__ = 'Jonarzz'

"""Module that contains all the methods used to prepare the memes database."""
# TODO: append new meme definitions to the database


import re
import sqlite3


def create_meme_database(filename):
    """Method that creates meme SQLite database with pairs meme-links based on filename of file
    containing reddit post with the meme list."""
    meme_dictionary = create_meme_dictionary(filename)

    conn = sqlite3.connect('../meme.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS memes (meme text, links text)')
    for key, value in meme_dictionary.items():
        c.execute("INSERT INTO memes VALUES (?, ?)", [key, value])

    conn.commit()
    conn.close()

def create_meme_dictionary(filename):
    """Method that returns a dictionary of pairs "meme text" : "links".
    Links are separated with " | " characters, if there is more than 1 link for a meme."""

    file_content = read_from_file(filename)
    matches_list = re.findall('<p>([^<>]*?)(<a.*?)</p>', file_content, re.DOTALL | re.UNICODE)

    meme_dictionary = {}
    for match in matches_list:
        for meme in re.split(';|(?<!_)\.(?!(_|\d))', match[0].lower()):
            if meme:
                meme = meme.strip()
                if meme != '':
                    meme_dictionary[meme] = get_links_from_match(match[1])

    return meme_dictionary

def read_from_file(filename):
    """Method that takes filename as an argument and returns contant of the file as string"""
    with open(filename, 'r', encoding="utf8") as f:
        return f.read()


def get_links_from_match(match):
    """Method that returns a string with links separated with " | " characters" out of a string
    in such a format: <a (...)</a>"""
    return ' | '.join(re.findall('<a.*?href="(.*?)".*?</a>', match))


create_meme_database("AuroraProxy-s-post.txt")
