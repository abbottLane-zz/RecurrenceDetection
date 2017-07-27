import os
import subprocess
from subprocess import Popen, PIPE, STDOUT


class MetaMap:
    def __init__(self, path):
        self.path=path

    def map_concepts(self, concepts):
        '''
        Given a list [str2, str2, str3, ...], start a subprocess to transform list of strings to
         a dictionary of a list of UMLS concepts.
        :param concepts: [str1, str2, str3, ...]
        :return:Dict: {str1:list[UMLSConcept1, UMLSConcept2, UMLSConcept3, ...]}
        '''
        # Make subprocess call, capture output
        result_dict = dict()
        for concept in concepts:
            if concept not in result_dict:
                p = Popen([os.path.join(self.path, 'metamaplite.sh'), '--pipe'], stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=self.path)
                stdout_data = p.communicate(bytes(concept, encoding='utf-8'))
                result_dict[concept] = self._build_umls_concepts(str(stdout_data[0], 'utf-8'))
        return result_dict

    def _build_umls_concepts(self, mm_output):
        '''
        Given raw input from the subprocess call to metamap, return a list of concept dictionaries:
        list[{'text':_, 'sem_class':_, 'start':_, 'end':_ 'cui':_},
             {'text':_, 'sem_class':_, 'start':_, 'end':_ 'cui':_},
             ...
            ]
        :param output: text output from metamap subcall
        :return: list of umls concept dictionaries
        '''
        #account for edge case where mm output is empty string
        if mm_output == "":
            return list()

        concept_dict_list = list()
        individual_concepts = mm_output.split('\n')
        for concept in individual_concepts:
            if concept != "":
                concept_dict=dict()
                items = concept.split("|")
                if len(items) <= 1: # accounts for garbage input not in the correct format
                    return list()
                concept_dict['desc'] = items[3]
                concept_dict['sem_class'] = items[5].lstrip('[').rstrip(']')
                concept_dict['span'] = self._parse_indices(items[7])
                concept_dict['cui'] = items[4]
                concept_dict_list.append(concept_dict)
        return concept_dict_list

    def _parse_indices(self, param):
        '''
        :param param: a list of indices: could be '0/11' or have multiple entries like '0/11,14/11'
        :return:
        '''
        begin_end=list()
        items = param.split(',')
        for i in items:
            begin_end.append((int(i.split("/")[0]),int(i.split("/")[1]) + int(i.split("/")[0])))
        return begin_end