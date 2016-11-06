## bittrex.py
Get current Bittrex market data and store in a local db

Note: During the first run you must specify the -i (init) flag to create the database

example run:
```
$ ./bittrex.py -m BTC-FTC -p

Market   Time           Buyq    Sellq Bid         Ask         Buy# Sell#     Buy min   Sell max
BTC-FTC  1458192319   117141   336303 0.00001914  0.00001996   158   523  0.00001666 0.00003810
BTC-FTC  1458192320   117141   336303 0.00001914  0.00001996   158   523  0.00001666 0.00003810
BTC-FTC  1458192423   117141   336303 0.00001914  0.00001996   158   523  0.00001666 0.00003810
BTC-FTC  1458192864   101245   298172 0.00001924  0.00001987   155   522  0.00001666 0.00003850
```
options:
```
$ ./bittrex.py -h

usage: ./bittrex.py [-iph] -m market
   eg: ./bittrex.py -m BTC-ETH

     -i [--init]     initializes a new sqlite database 'market.db'
     -p [--print]    prints out history for given market
     -m [--market]   specifies the market to use
     -h [--help]     prints this menu
```


---
