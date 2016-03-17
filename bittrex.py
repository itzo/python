#!/usr/bin/env python

# author:       me@itzo.org
# version:      2.1
# description:  Get current data from bittrex for market exchange rates and amounts in order book
# usage:        ./bittrex.py BTC-ETH

import urllib
import json
import datetime
import sys
import getopt
import sqlite3 as db

def usage():
    print "usage: ./bittrex.py [-iph] -m market"
    print "     -i [--init]     initializes a new sqlite database 'market.db'"
    print "     -p [--print]    prints out history for given market"
    print "     -m [--market]   specifies the market to use (e.g. BTC-SJCX)"
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

# get cmd line options
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
        required_m = True
    elif opt in ('-i', '--init'):
        create_db()
    elif opt in ('-p', '--print'):
        print "print history of market"
    else:
        usage()
        sys.exit(2)
if required_m == False:
    usage()
    sys.exit(2)


#market = sys.argv[1]
date = datetime.datetime.now()
url = 'https://bittrex.com/api/v1.1/public/getorderbook?market='+market+'&type=both&depth=50'

# load json data
json_obj = urllib.urlopen(url)
data = json.load(json_obj)

# initiate buy and sell quantity
buyq = 0
sellq = 0
# only top 'percent' % of each orderbook considered relevant data
percent = 25
# or use buy_index and sell_index instead
#buy_index = 40
#sell_index = 50

print "----------------------------------------"
bid = data['result']['buy'][0]['Rate']
total_buy_orders = len(data['result']['buy'])
print "buy orders:\t\t"+str(total_buy_orders)
buy_index = percent*total_buy_orders/100
print "buy_index:\t\t"+str(buy_index)
buy_min = data['result']['buy'][buy_index]['Rate']
print "MIN buy allowed:\t"+str(buy_min)
print "----------------------------------------"
ask = data['result']['sell'][0]['Rate']
total_sell_orders = len(data['result']['sell'])
print "sell orders:\t\t"+str(total_sell_orders)
sell_index = percent*total_sell_orders/100
print "sell_index:\t\t"+str(sell_index)
sell_max = data['result']['sell'][sell_index]['Rate']
print "MAX sell allowed:\t"+str(sell_max)
print "----------------------------------------"

# get the sum of all orders that we care about
for item in data['result']['buy']:
        if item['Rate'] > buy_min:
            buyq += item['Quantity']
for item in data['result']['sell']:
        if item['Rate'] < sell_max:
            sellq += item['Quantity']

# update the db with the latest info
def db_insert(market,buyq,sellq,bid,ask,total_buy_orders,total_sell_orders,buy_min,sell_max):
    timestamp = int(datetime.datetime.now().strftime("%s"))
    con = db.connect('market.db')
    cur = con.cursor()
    cur.execute('INSERT INTO history VALUES(?,?,?,?,?,?,?,?,?,?)', \
        (market,timestamp,int(buyq),int(sellq),bid,ask,total_buy_orders,total_sell_orders,buy_min,sell_max));
    con.commit()

db_insert(market,buyq,sellq,bid,ask,total_buy_orders,total_sell_orders,buy_min,sell_max)
