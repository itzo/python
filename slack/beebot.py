import os
import time
from slackclient import SlackClient
import sqlite3 as db
import sys
import re

channel = '#general'

# BOT_ID = os.environ.get('BOT_ID')

# crate db table
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
                counter INTEGER
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
    print str(event) + '\n'
    if event and len(event) > 0:

        # process reactions
        data = event[0]
        if all(x in data for x in ['user', 'item_user', 'reaction']):
            reaction = data['reaction']
            from_user = data['user']
            to_user = data['item_user']
            if data['type'] == 'reaction_added':
                print "%s reacted with '%s' to %s" % (from_user, reaction, to_user)
                counter = '1'
                db_insert(from_user, to_user, reaction, counter)
            elif data['type'] == 'reaction_removed':
                print "%s withdrew his reaction of '%s' from %s" % (from_user, reaction, to_user)
                counter = '-1'
                db_insert(from_user, to_user, reaction, counter)
            return reaction, from_user, to_user

        # answer commands
        if 'text' in data:
            if data['text'].startswith('showme top'):
                if len(data['text'].split()) > 2:
                    reaction = data['text'].split()[2]
                    if re.match(r'^[A-Za-z0-9_]+$', reaction):
                        print_top(reaction)
                        #if len(response) < 1:
                        #    response = 'Not sure we have these stats yet...'
                        #sc.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
                    else:
                        bot_usage()
                else:
                    bot_usage()

    return None, None, None

def bot_usage():
    sc.api_call("chat.postMessage", channel=channel, text='usage: showme top <reaction>', as_user=True)

# print top X
def print_top(reaction):
    if os.path.isfile('reactions.db'):
        con = db.connect('reactions.db')
        with con:
            cur = con.cursor()
            cur.execute("SELECT to_user, sum(counter) as count from reactions where reaction='"+ reaction +"' group by to_user order by count desc limit 5;")
            con.commit()
            rows = cur.fetchall()
            print "%-14s %+14s" % ('User', 'Count')
            response = "```{:14} {:>14}\n".format('user', 'count')
            for row in rows:
                print "%-14s %+14d" % (row[0], row[1])
                response += "{:14} {:14d}\n".format(row[0],row[1])
            response += "```"
            sc.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    else:
        print "Can't find the database.\n"
        sys.exit(2)


# get the list of users and their real names
def get_users():
    data = sc.api_call('users.list', channel='#general')
    for user in data['members']:
        print 'id: %s, name: %s' % (user['id'], user['name'])

# main
if __name__ == '__main__':
    # initialize db if it doesn't exist
    if os.path.exists('./reactions.db') == False:
        create_db()
    # connect to slack
    token = os.environ.get('SLACK_BOT_TOKEN')
    sc = SlackClient(token)
    if sc.rtm_connect():
        print('Bot connected and running!')
        #sc.api_call("chat.postMessage", channel=channel, text="beebot is back from the dead...", as_user=True)
        get_users()
        while True:
            reaction, from_user, to_user = parse_event(sc.rtm_read())
            time.sleep(1)
    else:
        print 'Connection failed. Check token.'
