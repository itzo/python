import os
import time
from slackclient import SlackClient
import sqlite3 as db
import pprint
import sys

# BOT_ID = os.environ.get('BOT_ID')

# initialize the reactions.db once
def create_db():
    try:
        con = db.connect('reactions.db')
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS reactions')
        cur.executescript("""
            CREATE TABLE reactions(
                from_user TEXT,
                to_user TEXT,
                reaction TEXT,
                counter TEXT
            );""")
        con.commit()
    except db.Error, e:
        if con:
            con.rollback()
        print "Error %s:" % e.args[0]
        sys.exit(1)
    finally:
        if con:
            con.close()

# insert reaction into db
def db_insert(from_user, to_user, reaction, counter):
    if os.path.isfile('reactions.db'):
        con = db.connect('reactions.db')
        cur = con.cursor()
        cur.execute('INSERT INTO reactions VALUES(?,?,?,?)', \
            (from_user, to_user, reaction, counter));
        con.commit()
    else:
        print "Can't find the database.\n"
        sys.exit(2)

# parse events for reactions
def parse_event(event):
    #print str(event) + '\n'
    if event and len(event) > 0:
        data = event[0]
        if 'reaction' in data:
            reaction = data['reaction']
            from_user = data['user']
            to_user = data['item_user']
            if data['type'] == 'reaction_added':
                print "%s reacted with '%s' to %s" % (from_user, reaction, to_user)
                counter = '+'
                db_insert(from_user, to_user, reaction, counter)
            elif data['type'] == 'reaction_removed':
                print "%s withdrew his reaction of '%s' from %s" % (from_user, reaction, to_user)
                counter = '-'
                db_insert(from_user, to_user, reaction, counter)
            return reaction, from_user, to_user
    return None, None, None

# get the list of users and their real names
def get_users():
    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(sc.api_call('users.list', channel='#general'))
    data = sc.api_call('users.list', channel='#general')
    for user in data['members']:
        print 'id: %s, name: %s' % (user['id'], user['name'])

# main
if __name__ == '__main__':
    if os.path.exists('./reactions.db') == False:
        create_db()
    token = os.environ.get('SLACK_BOT_TOKEN')
    sc = SlackClient(token)
    if sc.rtm_connect():
        print('Bot connected and running!')
        get_users()
        while True:
            reaction, from_user, to_user = parse_event(sc.rtm_read())
            time.sleep(1)
    else:
        print 'Connection failed. Check token.'