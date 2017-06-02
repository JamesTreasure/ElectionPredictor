#!/usr/bin/env python3

import urllib
import urllib.request
import urllib.error
import json
import datetime
import config

url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
app_key = config.app_key
session_token = config.session_token
headers = {'X-Application': app_key, 'X-Authentication': session_token, 'content-type': 'application/json'}
my_market_catalogue = []
list_of_market_ids = []


def call_aping(jsonrpc_req):
    try:
        req = urllib.request.Request(url, jsonrpc_req.encode('utf-8'), headers)
        response = urllib.request.urlopen(req)
        jsonResponse = response.read()
        return jsonResponse.decode('utf-8')
    except urllib.error.URLError as e:
        print(e.reason)
        print('Oops no service available at ' + str(url))
        exit()
    except urllib.error.HTTPError:
        print('Oops not a valid operation from the service ' + str(url))
        exit()


def get_event_types():
    event_type_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEventTypes", "params": {"filter":{ }}, "id": 1}'
    print('Calling listEventTypes to get event Type ID')
    eventTypesResponse = call_aping(event_type_req)
    eventTypeLoads = json.loads(eventTypesResponse)
    try:
        eventTypeResults = eventTypeLoads['result']
        return eventTypeResults
    except:
        print('Exception from API-NG' + str(eventTypeLoads['error']))
        exit()


def get_event_type_id_for_event_type_name(event_types_result, requested_event_type_name):
    if (event_types_result is not None):
        for event in event_types_result:
            event_type_name = event['eventType']['name']
            if (event_type_name == requested_event_type_name):
                return event['eventType']['id']
    else:
        print('Oops there is an issue with the input')
        exit()


def get_market_catalogue_for_politics(event_type_id):
    if (event_type_id is not None):
        print('Calling listMarketCatalouge Operation to get MarketID and selectionId')
        market_catalogue_req = '{ "jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": { "filter": { "eventTypeIds": ["' + event_type_id + '"],"marketCountries":["GB"], "textQuery":"Constituencies"},"maxResults":"650","marketProjection":["RUNNER_DESCRIPTION"]}}'
        market_catalogue_response = call_aping(market_catalogue_req)
        market_catalouge_loads = json.loads(market_catalogue_response)
        try:
            market_catalouge_results = market_catalouge_loads['result']
            print(len(market_catalouge_results))
            for market in market_catalouge_results:
                my_market_catalogue.append(market)
                list_of_market_ids.append(market['marketId'])
            return market_catalouge_results
        except:
            print('Exception from API-NG' + str(market_catalouge_results['error']))
            exit()


def printMyMarketCatalogue(market_catalogue):
    for market in market_catalogue:
        print('-------------------------------------------------------------------------------------')
        print('Constituency: ' + market['marketName'] + ', marketId: ' + market['marketId'])
        for runners in market['runners']:
            print(
                'Party: ' + runners['runnerName'] + ', selectionId: ' + str(runners['selectionId']) + ', price: ' + str(
                    runners.get('backPrice', None)))
        print('-------------------------------------------------------------------------------------')


def get_market_book_best_offers(marketId):
    market_book_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook", "params": {"marketIds":["' + marketId + '"],"marketProjection":["RUNNER_METADATA"],"priceProjection":{"priceData":["EX_BEST_OFFERS"]}}, "id": 1}'
    market_book_response = call_aping(market_book_req)
    market_book_loads = json.loads(market_book_response)
    try:
        market_book_result = market_book_loads['result']
        return market_book_result
    except:
        print('Exception from API-NG' + str(market_book_result['error']))
        exit()


def add_price_data(selectionId, backPrice, layPrice, tradedVolume, marketId):
    for market in my_market_catalogue:
        for runner in market['runners']:
            if (runner['selectionId'] == selectionId and market['marketId'] == marketId):
                runner['backPrice'] = float(backPrice)
                runner['layPrice'] = float(layPrice)
                runner['tradedVolume'] = tradedVolume


def get_price_info(market_book_result):
    for market_book in market_book_result:
        runners = market_book['runners']
        for runner in runners:
            if (runner['status'] == 'ACTIVE' and 'availableToBack' in runner['ex'] and 'availableToLay' in runner[
                'ex']):
                try:
                    max_back_price = max(item['price'] for item in runner['ex']['availableToBack'])
                except ValueError:
                    max_back_price = 0
                try:
                    max_lay_price = max(item['price'] for item in runner['ex']['availableToLay'])
                except ValueError:
                    max_lay_price = 0
                add_price_data((runner['selectionId']), str(max_back_price), str(max_lay_price),
                               str(runner['ex']['tradedVolume']), market_book['marketId'])
            else:
                print('This runner is not active or has no back price')


eventTypesResult = get_event_types()
politicsEventTypeId = get_event_type_id_for_event_type_name(eventTypesResult, 'Politics')

market_catalogue_result = get_market_catalogue_for_politics(politicsEventTypeId)

market_book_result_holder = []
for x in range(0, len(my_market_catalogue)):
    market_book_result_holder.append((get_market_book_best_offers(my_market_catalogue[x]['marketId'])))

for market_book_result in market_book_result_holder:
    (get_price_info(market_book_result))

date = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

with open(date + '.json', 'w') as f:
    json.dump(my_market_catalogue, f)
