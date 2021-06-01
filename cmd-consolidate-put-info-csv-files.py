#!/usr/bin/env python

import csv
import numpy as np
import pandas as pd


# I have one csv file with the stock symbols and the previous close.
# "symbol","company_name","previous_close"
# "AA","American Airlines",10.47

market_info = pd.read_csv('data/data-previous-close.csv', index_col='symbol')
market_info = market_info[['previous_close']]
market_info.head(n=1)

# I have 26 csv files with option information. They have these fields.
# chain_id
# chain_symbol
# created_at
# expiration_date
# id
# issue_date
# min_ticks
# rhs_tradability
# state
# strike_price
# tradability
# type
# updated_at
# url
# sellout_datetime
# adjusted_mark_price
# ask_price
# ask_size
# bid_price
# bid_size
# break_even_price
# high_price
# instrument
# instrument_id
# last_trade_price
# last_trade_size
# low_price
# mark_price
# open_interest
# previous_close_date
# previous_close_price
# volume
# symbol
# occ_symbol
# chance_of_profit_long
# chance_of_profit_short
# delta
# gamma
# implied_volatility
# rho
# theta
# vega
# high_fill_rate_buy_price
# high_fill_rate_sell_price
# low_fill_rate_buy_price
# low_fill_rate_sell_price


#
# Concatenate 26 csv files.
#

dfs = []
for x in range(ord('A'), ord('Z')+1):
    dfs.append(pd.read_csv(f'data/data-02-option_data.{chr(x)}.csv'))
df = pd.concat(dfs)

# Reject call options
df = df[df.type == 'put']

# Focus on just a few columns
df = df[['symbol', 'expiration_date', 'strike_price', 'mark_price', 'bid_price', 'bid_size']]

# Add previous close column
df = df.join(market_info, on='symbol')

# Only look at options expiring in the next month.
from datetime import datetime, timedelta
today = datetime.now()
one_month_out = today + timedelta(days=30)
df = df[df.expiration_date < one_month_out.strftime('%Y-%m-%d')]

#
# Add an in-the-money column.
#
df['itm'] = df.strike_price < df.previous_close

# Sort so that printing make sense.
df.sort_values(by=['symbol', 'expiration_date', 'strike_price'], ascending=[True, True, False], inplace=True)
df.reset_index(drop=True, inplace=True)

df.to_csv(f'data/symbol-exp-strike-mark-closing.csv', header=True, index=False, quoting=csv.QUOTE_NONNUMERIC)

print(df.head())
df.to_csv('data-lcs-input.csv', header=True, index=False, quoting=csv.QUOTE_NONNUMERIC)
df.head()
print('CSV created: data-lcs.csv')
