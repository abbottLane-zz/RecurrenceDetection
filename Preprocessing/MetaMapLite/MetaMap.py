import os
import subprocess


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
                output = subprocess.check_output(
                    [os.path.join(self.path, 'metamaplite.sh'), '--pipe'],
                    input=bytes(concept, encoding='utf-8')
                )
                result_dict[concept] = self._build_umls_concepts(str(output, 'utf-8'))
        return result_dict

    def _build_umls_concepts(self, output):
        '''
        Given raw input from the subprocess call to metamap, return a list of concept dictionaries:
        list[{'text':_, 'sem_class':_, 'start':_, 'end':_ 'cui':_},
             {'text':_, 'sem_class':_, 'start':_, 'end':_ 'cui':_},
             ...
            ]
        :param output: text output from metamap subcall
        :return: list of umls concept dictionaries
        '''
        concept_dict_list = list()
        individual_concepts = output.split('\n')
        for concept in individual_concepts:
            if concept != "":
                concept_dict=dict()
                items = concept.split("|")
                concept_dict['desc'] = items[2]
                concept_dict['sem_class'] = items[4].lstrip('[').rstrip(']')
                concept_dict['start'] = int(items[7].split(":")[0])
                concept_dict['end'] = int(items[7].split(":")[1]) + int(items[7].split(":")[0])
                concept_dict['cui'] = items[3]
                concept_dict_list.append(concept_dict)
        return concept_dict_list