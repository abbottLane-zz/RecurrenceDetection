import json

import requests


class NERData:
    def __init__(self):
        self.ner_api_url = 'https://nlp-brat-prod01.fhcrc.org/hutchner/ner_neg/crf'
        self.date_api_url = 'https://nlp-brat-prod01.fhcrc.org/hutchner/gen_ner/'
        self.api_headers = {"Content-Type: application/json"}


    def make_get_request(self, data, type="crf"):
        '''
        :param data: dictionary of {doc_id:text} in the form:
        data = {
        "1234":"the patient experienced no chest pressure or pain or dyspnea, or pain, or dyspnea"
        }
        :return: JSON response from HutchNER
        '''
        url=""
        if type =="crf":
            url = self.ner_api_url
        elif type =="date":
            url=self.date_api_url
        if url =="":
            raise ValueError("Get request type set to invalid value.")
        response = requests.get(url, json=data)
        json_response = json.loads(response.text)
        chunked_response = self._chunk_api_response(json_response)
        return chunked_response

    def print_response(self, response):
        '''
        Prints a HutchNER JSON response to stdout
        :param response:
        '''
        print(json.dumps(response, sort_keys=True, indent=2))

    def _chunk_api_response(self, response):
        docid_chunked_entities = dict()
        for doc_id, datum in response.items():
            if doc_id not in docid_chunked_entities:
                docid_chunked_entities[doc_id]=dict()
            i=0
            tokens = response[doc_id]['NER_labels']
            while i < len(tokens):
                first_tok = tokens[i]
                chunk = list()
                if i < len(tokens) and tokens[i]['label'] != "O"and 'negation' not in tokens[i]:
                    if tokens[i]['label'] not in docid_chunked_entities[doc_id]:
                        docid_chunked_entities[doc_id][tokens[i]['label']]=list()
                    while i < len(tokens) and tokens[i]['label'] != "O" and 'negation' not in tokens[i]:
                        if first_tok['label'] == tokens[i]['label']:
                            chunk.append(tokens[i])
                        i += 1

                    #transform chunk list dicts into single chunk dict
                    consolidated_chunk = dict()
                    consolidated_chunk['text'] = ' '.join(x['text'] for x in chunk)
                    consolidated_chunk['start'] = min([int(x['start']) for x in chunk])
                    consolidated_chunk['stop'] = max([int(x['stop']) for x in chunk])
                    #consolidated_chunk['confidence'] = max([float(x['confidence']) for x in chunk])
                    consolidated_chunk['label'] =first_tok['label']

                    docid_chunked_entities[doc_id][first_tok['label']].append(consolidated_chunk)
                else:
                    i+=1
        return docid_chunked_entities


