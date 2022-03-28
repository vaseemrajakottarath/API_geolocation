from random import random
import urllib.parse
from flask import Flask, request
import requests
from dicttoxml import dicttoxml
from helpers.config import ACCEPTED_OUTPUT_FORMATS, ERRORS_AND_MESSAGES, GOOGLE_GEOCODE_API_SECRET_KEY, GOOGLE_GEOCODE_API_URL


app = Flask(__name__)


@app.route('/getAddressDetails', methods=['POST'])
def getAddress():
    ''' Returns Co-ordinates either in json or xml'''
    request_body = request.json
    address = request_body.get('address')
    output_format = request_body.get('output_format')
    validation_error = check_validation_error(address, output_format)
    if validation_error is not None:
        return validation_error, 400

    google_geocode_base_url = GOOGLE_GEOCODE_API_URL
    url = f'{google_geocode_base_url}/json?address={urllib.parse.quote(address)}&key={GOOGLE_GEOCODE_API_SECRET_KEY}'

    response = requests.request("GET", url, headers={}, data={})
    response = response.json()

    if len(response.get("results")) <= 0:
        return ERRORS_AND_MESSAGES['ADDRESS_NOT_FOUND'], 400

    location_result = response.get('results')[0]

    formatted_address = location_result.get('formatted_address')
    location_data = location_result.get('geometry').get('location')

    latitude = location_data.get("lat")
    longitude = location_data.get("lng")

    coordinates_result = {
        "coordinates": {
            "lat": latitude,
            "lng": longitude
        },
        "address": formatted_address
    }

    if output_format == "xml":
        return dicttoxml(coordinates_result, attr_type=False), {'Content-Type': 'application/xml'}
    return coordinates_result


def check_validation_error(address, output_format):
    if not address:
        return ERRORS_AND_MESSAGES['ADDRESS_NOT_PROVIDED']
    if not isinstance(address, str):
        return ERRORS_AND_MESSAGES['INVALID_ADDRESS']
    if not output_format:
        return ERRORS_AND_MESSAGES['OUTPUT_FORMAT_NOT_PROVIDED']
    if not isinstance(output_format, str):
        return ERRORS_AND_MESSAGES['INVALID_OUTPUT_FORMAT']
    if output_format not in ACCEPTED_OUTPUT_FORMATS:
        return ERRORS_AND_MESSAGES['OUTPUT_FORMAT_NOT_ACCEPTED']
    return None

if __name__ == "__main__":
    
    app.run(debug=True)
