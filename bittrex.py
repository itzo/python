#!/usr/bin/env python

# author:       me@itzo.org
# version:      2.2
# description:  Get current data from Bittrex for market exchange rates and amounts in order book
#               Store the data in a sqlite database for future use

import urllib
import json
import datetime
import sys
import getopt
import sqlite3 as db
import os.path


# print usage
def usage():
    print "usage: ./bittrex.py [-iph] -m market"
    print "   eg: ./bittrex.py -m BTC-ETH"
    print
    print "     -i [--init]     initializes a new sqlite database 'market.db'"
    print "     -p [--print]    prints out history for given market"
    print "     -m [--market]   specifies the market to use"
    print "     -h [--help]     prints this menu"


# initialize the market.db if requested
def create_db():
    try:
        con = db.connect('market.db')
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS history')
        cur.executescript("""
            CREATE TABLE history(  market TEXT,
                date TIMESTAMP,
                buyq INT,
                sellq INT,
                bid REAL,
                ask REAL,
                buy_orders INT,
                sell_orders INT,
                buy_min REAL,
                sell_max REAL);""")
        con.commit()
    except db.Error, e:
        if con:
            con.rollback()
        print "Error %s:" % e.args[0]
        sys.exit(1)
    finally:
        if con:
            con.close()


# update the db with the latest info
def db_insert(market,buyq,sellq,bid,ask,total_buy_orders,total_sell_orders,buy_min,sell_max):
    if os.path.isfile('market.db'):
        timestamp = int(datetime.datetime.now().strftime("%s"))
        con = db.connect('market.db')
        cur = con.cursor()
        cur.execute('INSERT INTO history VALUES(?,?,?,?,?,?,?,?,?,?)', \
            (market,timestamp,int(buyq),int(sellq),bid,ask,total_buy_orders,total_sell_orders,buy_min,sell_max));
        con.commit()
    else:
        print "Can't find the database. Please specify the -i flag to create it.\n"
        usage()
        sys.exit(2)

# get the market data
def get_data(market):
    # load JSON data from Bittrex API
    url = 'https://bittrex.com/api/v1.1/public/getorderbook?market='+market+'&type=both&depth=50'
    json_obj = urllib.urlopen(url)
    data = json.load(json_obj)
    # get the sum of all orders that we care about
    buyq = 0
    sellq = 0
    # only top 'percent' % of each orderbook considered relevant data
    percent = 25
    bid = data['result']['buy'][0]['Rate']
    total_buy_orders = len(data['result']['buy'])
    buy_index = percent * total_buy_orders/100
    buy_min = data['result']['buy'][buy_index]['Rate']
    ask = data['result']['sell'][0]['Rate']
    total_sell_orders = len(data['result']['sell'])
    sell_index = percent * total_sell_orders/100
    sell_max = data['result']['sell'][sell_index]['Rate']
    for item in data['result']['buy']:
        if item['Rate'] > buy_min:
            buyq += item['Quantity']
    for item in data['result']['sell']:
        if item['Rate'] < sell_max:
            sellq += item['Quantity']
    db_insert(market,buyq,sellq,bid,ask,total_buy_orders,total_sell_orders,buy_min,sell_max)

    #print "----------------------------------------"
    #print "buy orders:\t\t"+str(total_buy_orders)
    #print "buy_index:\t\t"+str(buy_index)
    #print "MIN buy allowed:\t"+str(buy_min)
    #print "----------------------------------------"
    #print "sell orders:\t\t"+str(total_sell_orders)
    #print "sell_index:\t\t"+str(sell_index)
    #print "MAX sell allowed:\t"+str(sell_max)
    #print "----------------------------------------"


# print market history
def print_history(market):
    con = db.connect('market.db')
    with con:
        cur = con.cursor()
        cur.execute('SELECT * from history')
        con.commit()
        rows = cur.fetchall()
        print "%-8s %-10s %+8s %+8s %-10s  %-10s %+5s %+5s  %+10s %+10s" % \
        ('Market', 'Time', 'Buyq', 'Sellq', 'Bid', 'Ask', 'Buy#', 'Sell#', 'Buy min', 'Sell max')
        for row in rows:
            if row[0] == market:
                print "%-8s %s %+8s %+8s %0.8f  %0.8f %+5s %+5s  %0.8f %0.8f" % \
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                #market,timestamp,int(buyq),int(sellq),bid,ask,total_buy_orders,total_sell_orders,buy_min,sell_max


# get cmd line options a.k.a. main... ;\
required_m = False
try:
    opts, args = getopt.getopt(sys.argv[1:], 'ipm:h', ['init', 'print', 'market=', 'help'])
except getopt.GetoptError:
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        usage()
        sys.exit(2)
    elif opt in ('-m', '--market'):
        market = arg
        get_data(market)
        required_m = True
    elif opt in ('-i', '--init'):
        create_db()
    elif opt in ('-p', '--print'):
        print_history(market)
    else:
        usage()
        sys.exit(2)
if required_m == False:
    usage()
    sys.exit(2)
