#!/usr/bin/env python3

import urllib
import urllib.request
import urllib.error
import json
import datetime
import sys

url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
appKey = "1Pr16TKP0ZJ2Qupy"
sessionToken = "hnLfi4b6ZRjWhjE3ipIGZzrpiKH9ST5dTbYAMfk86mA="
headers = {'X-Application': appKey, 'X-Authentication': sessionToken, 'content-type': 'application/json'}
myMarketCatalogue = []
listOfMarketIds = []


def callAping(jsonrpc_req):
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


def getEventTypes():
    event_type_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEventTypes", "params": {"filter":{ }}, "id": 1}'
    print('Calling listEventTypes to get event Type ID')
    eventTypesResponse = callAping(event_type_req)
    eventTypeLoads = json.loads(eventTypesResponse)
    try:
        eventTypeResults = eventTypeLoads['result']
        return eventTypeResults
    except:
        print('Exception from API-NG' + str(eventTypeLoads['error']))
        exit()


def getEventTypeIDForEventTypeName(eventTypesResult, requestedEventTypeName):
    if (eventTypesResult is not None):
        for event in eventTypesResult:
            eventTypeName = event['eventType']['name']
            if (eventTypeName == requestedEventTypeName):
                return event['eventType']['id']
    else:
        print('Oops there is an issue with the input')
        exit()


def getMarketCatalogueForPolitics(eventTypeID):
    if (eventTypeID is not None):
        print('Calling listMarketCatalouge Operation to get MarketID and selectionId')
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        # market_catalogue_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": {"filter":{"eventTypeIds":["' + eventTypeID + '"],"marketCountries":["GB"],"marketTypeCodes":["WIN"],'\
        # '"marketStartTime":{"from":"' + now + '"}},"sort":"FIRST_TO_START","maxResults":"1","marketProjection":["RUNNER_DESCRIPTION"]}, "id": 1}'
        market_catalogue_req = '{ "jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": { "filter": { "eventTypeIds": ["' + eventTypeID + '"],"marketCountries":["GB"], "textQuery":"Constituencies"},"maxResults":"650","marketProjection":["RUNNER_DESCRIPTION"]}}'

        market_catalogue_response = callAping(market_catalogue_req)

        market_catalouge_loads = json.loads(market_catalogue_response)
        try:
            market_catalouge_results = market_catalouge_loads['result']
            print(len(market_catalouge_results))
            for market in market_catalouge_results:
                myMarketCatalogue.append(market)
                listOfMarketIds.append(market['marketId'])
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


def getMarketBookBestOffers(marketId):
    # print ('Calling listMarketBook to read prices for the Market with ID :' + marketId)
    market_book_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook", "params": {"marketIds":["' + marketId + '"],"marketProjection":["RUNNER_METADATA"],"priceProjection":{"priceData":["EX_BEST_OFFERS"]}}, "id": 1}'

    market_book_response = callAping(market_book_req)

    market_book_loads = json.loads(market_book_response)

    try:
        market_book_result = market_book_loads['result']
        return market_book_result
    except:
        print('Exception from API-NG' + str(market_book_result['error']))
        exit()


def addPriceData(selectionId, backPrice, layPrice, tradedVolume, marketId):
    for market in myMarketCatalogue:
        for runner in market['runners']:
            if (runner['selectionId'] == selectionId and market['marketId'] == marketId):
                runner['backPrice'] = float(backPrice)
                runner['layPrice'] = float(layPrice)
                runner['tradedVolume'] = tradedVolume


def getPriceInfo(market_book_result):
    for marketBook in market_book_result:
        # print('Getting price info')
        runners = marketBook['runners']
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
                # print('Selection id: ' + str(runner['selectionId']) + ', Max Price: ' + str(max_back_price))
                addPriceData((runner['selectionId']), str(max_back_price), str(max_lay_price),
                             str(runner['ex']['tradedVolume']), marketBook['marketId'])
            else:
                print('This runner is not active or has no back price')


eventTypesResult = getEventTypes()
politicsEventTypeId = getEventTypeIDForEventTypeName(eventTypesResult, 'Politics')

marketCatalogueResult = getMarketCatalogueForPolitics(politicsEventTypeId)

# market_book_result_holder = []
#
#
#
# market_book_result_holder.append((getMarketBookBestOffers(myMarketCatalogue[0]['marketId'])))
#



# print(json.dumps(myMarketCatalogue[0], indent=4, sort_keys=True))


market_book_result_holder = []
for x in range(0, len(myMarketCatalogue)):
    # print(x)
    market_book_result_holder.append((getMarketBookBestOffers(myMarketCatalogue[x]['marketId'])))

for market_book_result in market_book_result_holder:
    (getPriceInfo(market_book_result))

date = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

with open(date + '.json', 'w') as f:
    json.dump(myMarketCatalogue, f)
