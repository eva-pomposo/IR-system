"""
Base template created by: Tiago Almeida & Sérgio Matos
Authors: 

Tokenizer module

Holds the code/logic addressing the Tokenizer class
and implemetns logic in how to process text into
tokens.

"""
from utils import dynamically_init_class
import re
from nltk.stem import PorterStemmer


def dynamically_init_tokenizer(**kwargs):
    """Dynamically initializes a Tokenizer object from this
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
    

class Tokenizer:
    """
    Top-level Tokenizer class
    
    This loosly defines a class over the concept of 
    an index.

    """
    def __init__(self, **kwargs):
        super().__init__()
    
    def tokenize(self, text):
        """
        Tokenizes a piece of text, this should be
        implemented by specific Tokenizer sub-classes.
        
        Parameters
        ----------
        text : str
            Sequence of text to be tokenized
            
        Returns
        ----------
        object
            An object that represent the output of the
            tokenization, yet to be defined by the students
        """
        raise NotImplementedError()

        
class PubMedTokenizer(Tokenizer):
    """
    An example of subclass that represents
    a special tokenizer responsible for the
    tokenization of articles from the PubMed.

    """
    def __init__(self, 
                 minL, 
                 stopwords_path, 
                 stemmer,
                 *args, 
                 **kwargs):
        
        super().__init__(**kwargs)
        self.minL = minL if minL else 2
        self.stopwords_path = stopwords_path
        self.stemmer = PorterStemmer() if stemmer == "potterNLTK" else None

        # Create stop words set
        if self.stopwords_path:
            stopw_file = open(self.stopwords_path, "r")
            self.stopw = set([x.strip().lower() for x in stopw_file.readlines() if len(x.strip()) >= self.minL])
            stopw_file.close()

        print("init PubMedTokenizer|", f"{minL=}, {stopwords_path=}, {stemmer=}")
        if kwargs:
            print(f"{self.__class__.__name__} also caught the following additional arguments {kwargs}")

    def tokenize(self, content):
        terms = self.filter_stopw_and_stemming(self.create_tokens(content))
        # Return a dictionary with the terms as keys and a tuple (term frequency, positions) as values
        tf_pos = {}
        for i, token in enumerate(terms):
            if token in tf_pos:
                tf_pos[token] = (tf_pos[token][0] + 1, tf_pos[token][1] + f",{i}")
            else:
                tf_pos[token] = (1, str(i))
        return tf_pos

    # Method that receives the tuple from reader and creates the tokens for each pmid bearing the following rules:
    # Only alphanumeric tokens, with a hyphen in the middle of the token or not (that's what the regex does).
    # The length of the token should be more or equal than self.minL
    # The tokens should be normalized (all in lower case)
    # The return is a list of tokens
    def create_tokens(self, content):
        return [token.lower().strip('-_') for token in re.split("[^a-zA-Z0-9_-]", content) if len(token.strip('-_')) >= self.minL]

    # Method to filter the tokens by stopwords and perform their stemming using PorterStemmer
    # The return is a list finally containing the terms (tokens that passed through all steps of tokenization)
    # We know that this code is repetitive, but in order to avoid the if statements inside the for loop, we had to do it this way (efficiency over readability, in this case)
    def filter_stopw_and_stemming(self, tokens):
        if self.stopwords_path:
            if self.stemmer: # If the user passed a stopwords_path and a stemmer as arguments in CLI, apply both operations
                return [self.stemmer.stem(token) for token in tokens if token not in self.stopw]
            return [token for token in tokens if token not in self.stopw] # Elif there is no stemmer, filter only by stopwords
                
        if self.stemmer:
            return [self.stemmer.stem(token) for token in tokens] # If there is only a stemmer, apply only the stemming
        return tokens # If there is no stopwords_path and no stemmer, return the same tokens list received from the create_tokens method