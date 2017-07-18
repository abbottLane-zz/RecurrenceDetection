import json

import requests


class NERData:
    def __init__(self):
        self.api_url = 'https://nlp-brat-prod01.fhcrc.org/hutchner/ner_neg/crf'
        self.api_headers = {"Content-Type: application/json"}


    def make_get_request(self, data):
        '''
        :param data: dictionary of {doc_id:text} in the form:
        data = {
        "1234":"the patient experienced no chest pressure or pain or dyspnea, or pain, or dyspnea"
        }
        :return: JSON response from HutchNER
        '''
        response = requests.get(self.api_url, json=data)
        return json.loads(response.text)

    def print_response(self, response):
        '''
        Prints a HutchNER JSON response to stdout
        :param response:
        '''
        print(json.dumps(response, sort_keys=True, indent=2))


