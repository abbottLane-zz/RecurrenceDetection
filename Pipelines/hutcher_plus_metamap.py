import dataset
from Loading.DocLoader import DocumentCollection
from Preprocessing.Dates import date_finder
from Preprocessing.HutchNER.NERData import NERData
from Preprocessing.MetaMapLite.MetaMap import MetaMap
from sqlalchemy.exc import ProgrammingError





def main():
    db = dataset.connect("sqlite:///recurrence_training.db")
    c = DocumentCollection("/home/wlane/PycharmProjects/RecurrenceDetection/Data/test_set")
    data = c.get_documents()


    # get named entity data
    # get problems from hutchner
    hutchner = NERData()
    response = hutchner.make_get_request(data)

    # get dates from Datefinder
    dates = find_dates(data)

    # get problem labels from response
    problems_by_docid = dict()
    mm = MetaMap('/home/wlane/Applications/public_mm_lite/')

    count=0
    for doc_id, r in response.items():
        count+=1
        if 'problem' in r:
            problem_chunks = r['problem']
            problems_by_docid[doc_id] = combine_data(mm, problem_chunks)
            write_to_sqlite_db(db, doc_id, problems_by_docid[doc_id], "problems")
        if "date" in dates[doc_id]:
            date_chunks=dates[doc_id]['date']
            write_to_sqlite_db(db,doc_id, date_chunks, "dates")
        print("Processed ", doc_id, str(count) +"/" + str(len(response.keys())))


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

def find_dates(data):
    dt = date_finder.DateFinder()
    date_entries=dict()
    for did, text in data.items():
        if did not in date_entries:
            date_entries[did] = dict()
        date_entries[did]['date'] = list()
        for actual_date_string, indexes, captures in dt.extract_date_strings(text):
            if len(actual_date_string) > 1:
                date_entries[did]['date'].append({"start":indexes[0],
                                     "stop":indexes[1],
                                     "label":"Date",
                                     "text":actual_date_string,
                                     "doc_id": did})
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

