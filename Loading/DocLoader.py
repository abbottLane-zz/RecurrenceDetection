import os
from os.path import isfile, join


class DocumentCollection(object):
    def __init__(self, directory):
        self.directory = directory
        self.documents = self._load_documents_in_dir(directory)

    def get_documents(self):
        return self.documents

    def _load_documents_in_dir(self, directory):
        doc_dict = dict()
        all_files = [f for f in os.listdir(directory) if isfile(join(directory, f))]
        for file in all_files:
            with open(os.path.join(directory,file), "r") as f:
                doc_dict[file] = f.read()
        return doc_dict
