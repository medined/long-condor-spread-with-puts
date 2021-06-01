#!/usr/bin/env python

from RejectionTracker import RejectTracker
import csv
import numpy as np
import pandas as pd

rejection_tracker = RejectTracker()

def is_p4(record, p4_puts):
    key = f'{record.symbol}/{record.expiration_date}/{record.strike_price}'
    return key in p4_puts

def get_p4_puts(df):
    t2 = df[df.itm == True]
    t3 = t2.groupby(['symbol', 'expiration_date', 'itm']).max('strike_price')
    d = t3.to_dict()
    p4_puts = []
    for x in d['strike_price'].keys():
        symbol = x[0]
        expiration_date = x[1]
        strike_price = d['strike_price'][x]
        p4_puts.append(f'{symbol}/{expiration_date}/{strike_price}')
    return p4_puts

def has_at_least_three_otm_puts(df):
    df = df[df.itm == False]
    return df.shape[0] >= 3


def get_lcs_for_symbol_and_expiration_date(symbol, expiration_date, df):
        #
        # We need at least four puts for this long condor spread.
        #
        if df.shape[0] < 4:
            rejection_tracker.not_four_puts()
            return None

        #
        # We need at least three OTM puts for this long condor spread.
        #
        if not has_at_least_three_otm_puts(df):
            rejection_tracker.not_min_three_otm_puts()
            return None

        p4_puts = get_p4_puts(df)
        if len(p4_puts) == 0:
            rejection_tracker.no_p4_puts()
            return None

        t4 = df.copy()
        # This took two minutes
        t4['p1'] = False
        t4['p2'] = False
        t4['p3'] = False
        t4['p4'] = df.apply(is_p4, axis=1, args=(p4_puts))
        t4.reset_index(drop=True, inplace=True)

        p4_index = list(t4.columns).index('p4') + 1

        lcs = t4.copy()
        for i in lcs.itertuples():
            index = i[0]
            p4 = i[p4_index]
            if p4 == True:
                lcs.at[index-1, 'p3'] = True
                lcs.at[index-2, 'p2'] = True
                lcs.at[index-3, 'p1'] = True
        lcs = lcs[lcs[['p1','p2','p3','p4']].any(1)]
        lcs.drop(['itm'], axis=1, inplace=True)
        lcs.reset_index(drop=True, inplace=True)

        if lcs.shape[0] != 4:
            rejection_tracker.not_four_lcs()
            return None

        p4 = lcs.iloc[0]
        p3 = lcs.iloc[1]
        p2 = lcs.iloc[2]
        p1 = lcs.iloc[3]

        if p1.bid_price < .05:
            rejection_tracker.below_min_p1_mark()
            return None

        if p1.bid_size == 0:
            rejection_tracker.zero_bid_size()
            return None

        max_loss = round(p1.mark_price + p4.mark_price - p2.mark_price - p3.mark_price, 2)
        if max_loss == 0:
            max_loss = .05

        if p1.mark_price < .05:
            rejection_tracker.below_min_p1_mark()
            return None

        max_profit = p2.strike_price - p1.strike_price - max_loss
        ratio = round(max_profit/max_loss, 2)

        record = {
            'symbol': symbol,
            'expiration_date': expiration_date,
            'p1': p1.strike_price,
            'p2': p2.strike_price,
            'p3': p3.strike_price,
            'p4': p4.strike_price,
            'max_loss': round(max_loss*100, 2),
            'max_profit': round(max_profit*100, 2),
            'ratio': ratio,
        }
        return record

def main():
    df = pd.read_csv('data-lcs-input.csv')
    # df = df[df.symbol.str.startswith('A')]

    records = []

    t1 = df.groupby(['symbol', 'expiration_date'])
    # x is a tuple which has two elements, a tuple (symbol, expiration_date) and a dataframe.
    for x in t1:
        symbol = x[0][0]
        expiration_date = x[0][1]
        df = x[1]
        record = get_lcs_for_symbol_and_expiration_date(symbol, expiration_date, df)
        if record != None:
            print(record)
            records.append(record)

    df = pd.DataFrame(records)
    if df.shape[0] > 0:
        df.to_csv(f'data-lcs.csv', header=True, index=False, quoting=csv.QUOTE_NONNUMERIC)
        df.sort_values('ratio', inplace=True)

    print(df.head())
    print(rejection_tracker.reasons)

if __name__ == '__main__':
    main()
