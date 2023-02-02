"""
Base template created by: Tiago Almeida & Sérgio Matos
Authors: 

Reader module

Holds the code/logic addressing the Reader class
and how to read text from a specific data format.

"""

import os
from utils import dynamically_init_class
import json
import gzip


def dynamically_init_reader(**kwargs):
    """Dynamically initializes a Reader object from this
    module.

    Parameters
    ----------
    kwargs : Dict[str, object]
        python dictionary that holds the variables and their values
        that are used as arguments during the class initialization.
        Note that the variable `class` must be here and that it will
        not be passed as an initialization argument since it is removed
        from this dict.
    
    Returns
        ----------
        object
            python instance
    """
    return dynamically_init_class(__name__, **kwargs)


class Reader:
    """
    Top-level Reader class
    
    This loosly defines a class over the concept of 
    a reader.
    
    Since there are multiple ways for implementing
    this class, we did not defined any specific method 
    in this started code.

    """
    def __init__(self, 
                 path_to_collection:str, 
                 **kwargs):
        super().__init__()
        self.path_to_collection = path_to_collection
        
    
class PubMedReader(Reader):
    def __init__(self, 
                 path_to_collection:str,
                 **kwargs):
        super().__init__(path_to_collection, **kwargs)
        print("init PubMedReader|", f"{self.path_to_collection=}")
        self.JSON_FILE = gzip.open(self.path_to_collection, 'rb')
        if kwargs:
            print(f"{self.__class__.__name__} also caught the following additional arguments {kwargs}")
    
    def read(self):
        # Read compressed file line by line and return each document in a tuple: (pmid, title abstract)
        line = self.JSON_FILE.readline()
        # If there are no more lines to read, close the file and return a tuple None, None
        if not line:
            self.JSON_FILE.close()
            return None, None
        result = json.loads(line) # Else, load the line and store the pmid as an int to save memory
        return int(result['pmid']), " ".join([result['title'], result['abstract']]) # and both title and abstract as a unique string divided by a space

class QuestionsReader(Reader):
    def __init__(self, 
                 path_to_questions:str,
                 **kwargs):
        super().__init__(path_to_questions, **kwargs)
        # I do not want to refactor Reader and here path_to_collection does not make any sense.
        # So consider using self.path_to_questions instead (but both variables point to the same thing, it just to not break old code)
        self.path_to_questions = self.path_to_collection
        self.questions_file = open(self.path_to_questions, 'r') if os.path.exists(self.path_to_questions) else None # Open the questions file if it exists, else set it to None
        print("init QuestionsReader|", f"{self.path_to_questions=}")
        if kwargs:
            print(f"{self.__class__.__name__} also caught the following additional arguments {kwargs}")

    def read(self):
        # Read questions file line by line and return each question
        line = self.questions_file.readline()
        # If there are no more lines to read, close the file and return None
        if not line:
            self.questions_file.close()
            return None
        return line.rstrip("\n")

class QuestionsWithGSReader(Reader):
    def __init__(self, 
                 path_to_questions:str,
                 **kwargs):
        super().__init__(path_to_questions, **kwargs)
        # I do not want to refactor Reader and here path_to_collection does not make any sense.
        # So consider using self.path_to_questions instead (but both variables point to the same thing, it just to not break old code)
        self.path_to_questions = self.path_to_collection
        self.questions_file = open(self.path_to_questions, 'r') if os.path.exists(self.path_to_questions) else None # Open the questions file if it exists, else set it to None
        print("init QuestionsWithGSReader|", f"{self.path_to_questions=}")
        if kwargs:
            print(f"{self.__class__.__name__} also caught the following additional arguments {kwargs}")

    def read(self):
        # Read questions file line by line and return each question
        line = self.questions_file.readline()
        # If there are no more lines to read, close the file and return None
        if not line:
            self.questions_file.close()
            return None
        return json.loads(line)['query_text']