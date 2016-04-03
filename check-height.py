#!/usr/bin/env python

# author:       itzo <me@itzo.org>
# version:      1.0
# description:  Get the status (height) and speed of all nodes


import sqlite3 as db
import smtplib
import argparse
import datetime
import subprocess
import os.path


# get arguments and usage
def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('hostsfile',
        help='The file containing the hostnames/IPs to check (one per line).'
    )
    parser.add_argument('-i', '--init', action='store_true',
        help='Create (or recreate) the database.'
    )
    return parser

# parse and validate arguments
def parse_args():
    parser = get_parser()
    args = parser.parse_args()
    if args.init == True:
        create_db()
    return args

# initialize the db if requested
def create_db():
    try:
        con = db.connect('status.db')
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS height')
        cur.executescript("""
            CREATE TABLE height(
                date TIMESTAMP,
                node TEXT,
                height INT);""")
        con.commit()
    except db.Error, e:
        if con:
            con.rollback()
        print "Error %s:" % e.args[0]
        sys.exit(1)
    finally:
        if con:
            con.close()

# get list of hosts from input file
def get_hosts(args):
    with open(args.hostsfile, 'r') as f:
        hosts = [line.rstrip('\n') for line in f]
    return hosts

# connect to each host to pull the data
def get_data(hosts):
    data = {}
    for node in hosts:
        cmd = "ssh " + node + " 'ls /mnt/acd/" + node + " | wc -l'"
        out = subprocess.check_output(cmd, shell=True)
        #print node + ": " + out.rstrip('\n') 
        data[node] = out.rstrip('\n')
    return data


# update the db with the latest data
def db_insert(latest_data):
  timestamp = 0
  for node,height in latest_data.iteritems():
    if os.path.isfile('status.db'):
        timestamp = int(datetime.datetime.now().strftime("%s"))
        con = db.connect('status.db')
        cur = con.cursor()
        cur.execute('INSERT INTO height VALUES(?,?,?)', \
            (timestamp,node,height));
        con.commit()
    else:
        print "Can't find the database. Please specify the -i flag to create it.\n"
        usage()
        sys.exit(2)
  print "current timestamp: " + str(timestamp)


# print height speed
def print_speed(hosts):
    con = db.connect('status.db')
    with con:
        cur = con.cursor()
        # let the dirty sql begin
        cur.execute("""
            select
            (select date from height as dd where dd.node = s.node and dd.date > s.date) -
            (select date from height as dd where dd.node = s.node and dd.date >= s.date) as date,
            node,
            (select height from height as hh where hh.node = s.node and hh.height > s.height) -
            (select height from height as hh where hh.node = s.node and hh.height >= s.height) as built,
            height
            from height s
              where (
                select count(*) from height f
                  where f.node = s.node
                  and f.date >= s.date
              ) <= 2
            order by date desc;
        """)
        con.commit()
    rows = cur.fetchall()
    print "%-12s %-6s %-8s %-8s" % ('Time Passed', 'Node', 'Built', 'Height')
    for row in rows:
        if row[0] > 0:
            print "%-12s %-6s %-8s %-8s" % (row[0], row[1], row[2], row[3])


# main function
def main():
    args = parse_args()
    hosts = get_hosts(args)
    latest_data = get_data(hosts)
    db_insert(latest_data)
    print_speed(hosts)

if __name__ == "__main__":
    main()

