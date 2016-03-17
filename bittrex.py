#!/usr/bin/env python

# version:     2.0
# description: get current data from bittrex for market exchange rates and amounts in order book
# example:     ./bittrex.py BTC-ETH

import urllib
import json
import datetime
import sys

market = sys.argv[1]
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

# print results
print "date      buyq  sellq bid    ask    buy# sell# min_buy max_sell"
print "%s/%s/%s" % (date.month, date.day, date.year),\
        str(int(buyq)),\
        str(int(sellq)),\
        str(bid),\
        str(ask),\
        str(total_buy_orders),\
        str(total_sell_orders),\
        str(buy_min),\
        str(sell_max)


