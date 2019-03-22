#!/usr/bin/env python
"""
Query the Knowledge Graph API https://developers.google.com/knowledge-graph/

"""

import argparse
import datetime
import requests
import json
import urllib
import config


def google_search(query):
    api_key = config.GOOGLE_KEY
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'

    params = {
        'query': query,
        'limit': 5,
        'indent': True,
        'key': api_key,
        }

    result_strings = []
    url = service_url + '?' + urllib.parse.urlencode(params)  # TODO: use requests
    response = json.loads(urllib.request.urlopen(url).read())

    # Parsing the response  TODO: log all responses
    print('Displaying results...' + ' (limit: ' + str(params['limit']) + ')\n')
    for element in response['itemListElement']:
        try:
            types = str(", ".join([n for n in element['result']['@type']]))
        except KeyError:
            types = "N/A"

        try:
            desc = str(element['result']['description'])
        except KeyError:
            desc = "N/A"

        try:
            detail_desc = str(element['result']['detailedDescription']['articleBody'])
        except KeyError:
            detail_desc = "N/A"

        try:
            mid = str(element['result']['@id'])
        except KeyError:
            mid = "N/A"

        try:
            url = str(element['result']['url'])
        except KeyError:
            url = ""

        try:
            score = str(element['resultScore'])
        except KeyError:
            score = "N/A"

        try:
            result_strings.append("*" + element['result']['name'] + '* - ' + '_' + desc + '_. ' + detail_desc + ' Find out more - ' + url)
        except:
            result_strings.append("Sorry! Coudn't find anything!")
            break

    return result_strings


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('query', help='The search term to query')
    args = parser.parse_args()
    res = google_search(args.query)
    for r in res:
        print(r)