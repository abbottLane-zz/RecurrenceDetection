import dataset
import re

from Loading.DocLoader import DocumentCollection
from Preprocessing.Dates import date_finder
from Preprocessing.HutchNER.NERData import NERData
from Preprocessing.MetaMapLite.MetaMap import MetaMap
from sqlalchemy.exc import ProgrammingError
import en_core_web_sm



def main():
    spacy_model = en_core_web_sm.load()
    db = dataset.connect("sqlite:///recurrence_training.db")
    c = DocumentCollection("/home/wlane/PycharmProjects/RecurrenceDetection/Data/test_set")
    data = c.get_documents()

    # get problems from hutchner
    hutchner = NERData()
    response = hutchner.make_get_request(data)

    # get sentences from a spacy parse
    sentence_data =data2sentences(data, spacy_model)

    # get candidates for disease status/metastisis
    problems_by_docid = dict()
    mm = MetaMap('/home/wlane/Applications/public_mm_lite/')
    count=0
    status_candidates_by_doc_id=dict()
    for doc_id, r in response.items():
        count+=1
        if 'problem' in r:
            problem_chunks = r['problem']
            problems_by_docid[doc_id] = combine_data(mm, problem_chunks)
        print("Processed ", doc_id, str(count) +"/" + str(len(response.keys())))
        neoplasms_and_dates = predict_has_status(problems_by_docid[doc_id], sentence_data[doc_id])
        status_candidates_by_doc_id[doc_id] = _select_dates_per_entity(neoplasms_and_dates)


    # TODO: train/predict status classification based on entity and its context (svm)
    return status_candidates_by_doc_id

def _select_dates_per_entity(data):
    '''
    select single date (or no date) per entity, assemble appropriate context for determining status
    :param data:
    :return: {entity:entity_dict, date:date_dict, context:"context string." }
    '''
    training_contexts=list()
    for datum in data:
        date=[]
        context=list()
        context.append(datum['sentence_context']['current'])
        if len(datum['dates']['current']) > 0:
            date = datum['dates']['current']
        elif len(datum['dates']['last']) >0:
            date = datum['dates']['last']
            context.append(datum['sentence_context']['last'])
        elif len(datum['dates']['next']) > 0:
            date = datum['dates']['last']
            context.append(datum['sentence_context']['next'])
        training_contexts.append({"data":datum, 'date':date, 'context':' '.join([c.string for c in context])})
    return training_contexts

def data2sentences(data, model):
    doc_id_sentence_data = dict()
    for doc_id, text in data.items():
        doc = model(text)
        sentences = [sent for sent in doc.sents] #.string.strip()
        doc_id_sentence_data[doc_id] = sentences
    return doc_id_sentence_data


def predict_has_status(problem_chunks,sentences):
    neoplasms_w_dates = list()
    for surf_str, problems in problem_chunks.items():
        for entry in problems:
            if entry['sem_class']=="neop":
                sentence_context =sentence_context_from_problem(entry, sentences, start=0, end=len(sentences)-1)
                date_chunks=get_dates(sentence_context)
                entry.update(dates=date_chunks, sentence_context=sentence_context)
                neoplasms_w_dates.append(entry)
    return neoplasms_w_dates


def sentence_context_from_problem(problem, sentences, start, end):
    '''
    given a problem with is span, find the sentence it belongs to.
    Sentences sorted in ascending order. Do binary search for correct sentence.
    :param problem:
    :return: a spacy Span object
    '''
    midpoint = int((start + end)/2)
    # if problem DOES occur in this sentence
    if problem['span'][0][0] >= sentences[midpoint].start_char and \
        problem['span'][0][1] <= sentences[midpoint].end_char:
        current = sentences[midpoint]
        last=""
        next=""
        if midpoint-1 > 0 :
            last = sentences[midpoint-1]
        if midpoint +1 < len(sentences):
            next = sentences[midpoint+1]
        return {'current':current, 'last':last, 'next':next}

    else:
        #detrermine whether to go higher or lower
        if problem['span'][0][0] < sentences[midpoint].start_char and \
                        problem['span'][0][1] < sentences[midpoint].start_char:
            # jump into the lower half
            return sentence_context_from_problem(problem, sentences, start, midpoint)

        elif problem['span'][0][0] > sentences[midpoint].end_char and \
                        problem['span'][0][1] > sentences[midpoint].end_char:
            # jump into the upper half
            return sentence_context_from_problem(problem, sentences, midpoint, end)


def write_to_sqlite_db(db,did, dict_of_ents, table_text):
    table = db[table_text]
    if table_text == "problems":
        try:
            for st, problem_string_entries in dict_of_ents.items():
                for pse in problem_string_entries:
                    pse['span'] = str(pse['span'])
                    pse.update(dict(doc_id=did))
                    pse.update(dict(problem_string=st))
                    table.insert(pse)
        except ProgrammingError as err:
            print(err)
    elif table_text =="dates":
        try:
            for dse in dict_of_ents:
                dse.update(dict(doc_id=did))
                table.insert(dse)
        except ProgrammingError as err:
            print(err)
    pass

def get_dates(sent_objs):
    current = sent_objs['current']
    last = sent_objs['last']
    next = sent_objs['next']

    curr_date_entries = get_dates_from_text(current)
    last_date_entries = get_dates_from_text(last)
    next_date_entries = get_dates_from_text(next)

    return {'current':curr_date_entries,
            'last':last_date_entries,
            'next':next_date_entries}

def get_dates_from_text(sent_obj):
    if not sent_obj: return []
    dt = date_finder.DateFinder()
    date_entries = list()
    offset= sent_obj.start_char
    text = sent_obj.text
    for actual_date_string, indexes, captures in dt.extract_date_strings(text):
        if len(actual_date_string) > 1 and re.match("\d+", actual_date_string):
            if not re.match("^\d{1,3}$", actual_date_string):
                date_entries.append({"start": indexes[0] + offset,
                                 "stop": indexes[1] + offset,
                                 "text": actual_date_string
                                 })
    return date_entries

def combine_data(mm, problem_chunks):
    mm_entities = mm.map_concepts([x['text'] for x in problem_chunks])
    combined_data = combine_HutchNER_and_Metamap_data(problem_chunks, mm_entities)
    return combined_data

def combine_HutchNER_and_Metamap_data(problem_chunks, mm_entities):
    for problem in problem_chunks:
        if problem['text'] in mm_entities:
            current = mm_entities[problem['text']]
            for datum in current:
                for i, span in enumerate(datum['span']):
                    newbegin = span[0] + problem['start']
                    newend = span[1] + problem['start']
                    datum['span'][i] = (newbegin,newend)
    return mm_entities

if __name__ == "__main__":
    main()

