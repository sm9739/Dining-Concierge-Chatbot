from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib
import boto3
import decimal
import csv

try:
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


API_KEY= '<API_KEY>' 

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'


DEFAULT_TERM = 'korean restaurants'
DEFAULT_LOCATION = 'Manhattan'
SEARCH_LIMIT = 50

def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }
    print(u'Querying {0} ...'.format(url))
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()


def search(api_key, term, location, offSet):

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
         'offset': offSet,
         'limit': SEARCH_LIMIT        
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def getTotal(api_key, term, location):

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
         #'offset': offSet,
         'limit': SEARCH_LIMIT        
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params).get('total')


def get_business(api_key, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id
    return request(API_HOST, business_path, api_key)


def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    list1 = []
    list1.append("ID")
    list1.append("Name")
    list1.append("Address")
    list1.append("Coordinates")
    list1.append("NumOfReview")
    list1.append("Ratings")
    list1.append("Zipcode")
    list1.append("Cuisine")
    filename = "Manhattan_Restaurants"+ '.csv'
    with open(filename, "a", newline='', encoding='utf-8') as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(list1)

    cuisines = ['indian', 'chinese', 'italian', 'japanese', 'mexican', 'american', 'arab', 'thai', 'korean']
    for cuisine in cuisines:
        newterm = cuisine+ ' restaurants'
        total = getTotal(API_KEY, newterm, location)
        print(total, cuisine)
        run = 0
        maxOffSet = int(total / 50)
        businesses = []
        for offSet in range(0, maxOffSet+1):
            if run == 25:
                break
            response = search(API_KEY, newterm, location, offSet*50)
            if response.get('businesses') is None:
                break
            businesses.append(response.get('businesses'))
            run+=1

        printVar = []
        for buis in businesses:
            for b in buis:
                printVar.append(b)

        if not businesses:
            return

        for b in printVar:
            ID = b['id']
            Name = b['name']
            Address = ', '.join(b['location']['display_address'])
            NumOfReview = int(b['review_count'])
            Ratings = float(b['rating'])

            if (b['coordinates'] and b['coordinates']['latitude'] and b['coordinates']['longitude']):
                Coordinates = str(b['coordinates']['latitude'])+ ', '+str(b['coordinates']['longitude'])
            else:
                Coordinates = None

            if (b['location']['zip_code']):
                Zipcode = b['location']['zip_code']
            else:
                Zipcode = None

            temparr = []
            temparr.append(ID)
            temparr.append(Name)
            temparr.append(Address)
            temparr.append(Coordinates)
            temparr.append(NumOfReview)
            temparr.append(Ratings)
            temparr.append(Zipcode)
            temparr.append(cuisine)

            with open(filename, "a", newline='', encoding='utf-8') as fp:
                wr = csv.writer(fp, dialect='excel')
                wr.writerow(temparr)

        print("Added ",cuisine," restaurants")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=DEFAULT_LOCATION, type=str,
                        help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        query_api(input_values.term, input_values.location)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )

if __name__ == '__main__':
    main()
