#!/usr/bin/env python3
import difflib
import urllib
import json
import datetime
import sys
import csv
import operator

# begin = 3
# end = 4
#
# with open('seats.txt', "r") as file_in:
#     with open('output2.csv', "w") as file_out:
#         writer = csv.writer(file_out)
#         for row in csv.reader(file_in):
#             writer.writerow(row[begin:end])
#
# print('Done')


with open('17-06-08-22-06.json') as f:
    my_market_catalogue = json.load(f)


parties = set()
for market in my_market_catalogue:
    for runner in market['runners']:
        parties.add(runner['runnerName'])

seat_count = {}
for party in parties:
    seat_count[party] = 0

current_seats = {}
with open('seats.txt') as f:
    for line in f:
        a = line.rsplit(',', 1)
        current_seats[a[0]] = a[1].rstrip()

constituencies_processed = 0
number_of_ties = 0
lookups = 0

predicted_election_results = {}

for market in my_market_catalogue:
    print('---------------------')
    lowest_price_back = 10000
    lowest_price_back_candidate_name = None
    lowest_price_lay = 10000
    lowest_price_lay_candidate_name = None
    number_of_runners = len(market['runners'])
    print('Number of runners: ' + str(number_of_runners))
    back_number_of_runners_no_odds = 0
    lay_number_of_runners_no_odds = 0
    favourite_candidate = None
    for runner in market['runners']:
        try:
            if (runner['backPrice'] < lowest_price_back and runner['backPrice'] != 0.0):
                lowest_price_back = runner['backPrice']
                lowest_price_back_candidate_name = runner['runnerName']
            else:
                back_number_of_runners_no_odds += 1
        except KeyError:
            print('No backPrice at ' + str(runner) + ' in ' + market['marketName'])
        try:
            if (runner['layPrice'] < lowest_price_lay and runner['layPrice'] != 0.0):
                lowest_price_lay = runner['layPrice']
                lowest_price_lay_candidate_name = runner['runnerName']
            else:
                lay_number_of_runners_no_odds += 1
        except KeyError:
            print('No layPrice at ' + str(runner) + ' in ' + market['marketName'])

    if (lowest_price_back > 2.5 and lowest_price_lay > 2.5):
        lowest_price_back = 0.0
        lowest_price_lay = 0.0
        try:
            print("Looked up " + market['marketName'] + ' in dictionary and ' + str(
                current_seats.get(market['marketName']) + ' won last time.'))
            favourite_candidate = current_seats.get(market['marketName'])
        except:
            print("Error looking up " + market['marketName'])

    print('BACK: Lowest price runner is ' + str(lowest_price_back_candidate_name) + ' @ ' + str(
        lowest_price_back) + ' for ' + market['marketName'])
    print('LAY: Lowest price runner is ' + str(lowest_price_lay_candidate_name) + ' @ ' + str(
        lowest_price_lay) + ' for ' + market['marketName'])

    if (lowest_price_back < lowest_price_lay):
        favourite_candidate = lowest_price_back_candidate_name
    elif (lowest_price_back > lowest_price_lay):
        favourite_candidate = lowest_price_lay_candidate_name
    elif (lowest_price_back == lowest_price_lay):
        number_of_ties += 1
        try:
            print("Looked up " + market['marketName'] + ' in dictionary and ' + str(
                current_seats.get(market['marketName']) + ' won last time.'))
            favourite_candidate = current_seats.get(market['marketName'])
            lookups +=1
        except:
            print("Error looking up " + market['marketName'])

    if (lowest_price_back == 1.01):
        try:
            print("Looked up " + market['marketName'] + ' in dictionary and ' + str(
                current_seats.get(market['marketName']) + ' won last time.'))
            favourite_candidate = current_seats.get(market['marketName'])
            if(favourite_candidate == 'Conservatives'):
                lookups +=1
        except:
            print("Error looking up " + market['marketName'])


    if(favourite_candidate == 'Green' or favourite_candidate == 'UKIP'):
        try:
            print("Looked up " + market['marketName'] + ' in dictionary and ' + str(
                current_seats.get(market['marketName']) + ' won last time.'))
            favourite_candidate = current_seats.get(market['marketName'])
            if(favourite_candidate == 'Conservatives'):
                lookups +=1
        except:
            print("Error looking up " + market['marketName'])

    print('Favourite is ' + favourite_candidate)
    print('---------------------')
    predicted_election_results[market['marketName']] = favourite_candidate
    constituencies_processed += 1

    # if (lowest_price_back < lowest_price_lay and lowest_price_back != 0):
    #     favourite_candidate = lowest_price_back_candidate_name
    # elif (lowest_price_lay < lowest_price_back and lowest_price_lay != 0):
    #     favourite_candidate = lowest_price_lay_candidate_name

    for seat in seat_count:
        if (seat == favourite_candidate):
            seat_count[seat] += 1

print(constituencies_processed)
print(parties)
print(seat_count)
sorted_x = sorted(seat_count.items(), key=operator.itemgetter(1))
for s in sorted_x:
    print(s)





print(predicted_election_results)
with open('predicted_election_results.json', 'w') as f:
    json.dump(predicted_election_results, f)
