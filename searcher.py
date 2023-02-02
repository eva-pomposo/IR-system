import math
import os
import time
import math
from utils import dynamically_init_class
from itertools import islice

def dynamically_init_searcher(**kwargs):
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

class BaseSearcher:

    def search(self, index, query_tokens, top_k):
        pass

    def search_mwb(self, index, query_tokens, top_k, B):
        pass

    def batch_search(self, index, reader, tokenizer, output_file, top_k=1000, mwb=False, B=2):
        results_file = open(output_file, 'w') # open the file for writing
        print("searching...")
        # loop that reads the questions
        queries_exec_times = [] # list to store the execution time of each query
        question = reader.read() # read the first question
        while question: # while there are questions to read
            exec_time = time.time() # start counting the query execution time
            # search and write results to disk
            self.search_and_write_results(question, tokenizer, index, top_k, mwb, B, results_file)
            exec_time = time.time() - exec_time # calculate the query execution time
            queries_exec_times.append(exec_time)
            # read the next question
            question = reader.read()
        
        queries_exec_times = sorted(queries_exec_times) # sort the list of execution times
        if len(queries_exec_times) % 2 == 0: # if the list has an even number of elements, the median is the average of the two middle elements
            med_query_lat = (queries_exec_times[int((len(queries_exec_times) / 2) - 1)] + queries_exec_times[int((len(queries_exec_times) / 2))]) / 2
        else: # if the list has an odd number of elements, the median is the middle element
            med_query_lat = queries_exec_times[math.ceil(len(queries_exec_times) / 2) - 1]

        results_file.write('Median query latency: ' + str(med_query_lat) + ' sec')
        results_file.close()

    def interactive_search(self, index, reader, tokenizer, top_k=1000, mwb=False, B=2):
        results = {}
        query = input("Insert a query to search for (or 'q' to quit): ")
        while query != "q": # loop until the user enters 'q'
            if query != "": # if the user enters a query, save it and show the first 10 results for it
                results = self.search_and_write_results(query, tokenizer, index, top_k, mwb, B)
                print('Search results for question: ' + query)
            temporary_result_keys = []
            for doc_id, score in islice(results.items(), 10):
                print(f"docID: {doc_id}\t\tScore: {score}")
                temporary_result_keys.append(doc_id)
            [results.pop(doc_id) for doc_id in temporary_result_keys]
            if len(results.keys()) > 0: # if there are still results to show, ask the user if he wants to see more
                query = input("Press ENTER for more 10 results, or type another query to search for ('q' to quit): ")
            else:
                query = input("No more results to show for this query! Insert a new query to search for (or 'q' to quit): ")

    def search_and_write_results(self, question, tokenizer, index, top_k, mwb, B, results_file=""):
        # aplies the tokenization to get the query_tokens
        query_tokens = tokenizer.tokenize(question)

        # search the index
        results = self.search_mwb(index, query_tokens, top_k, B) if mwb else self.search(index, query_tokens, top_k)
        
        # write results to disk
        if results_file != "":
            results_file.write('Search results for question: ' + question + '\n') # write the question
            for doc_id, score in results.items():
                results_file.write(f"docID: {doc_id}\t\tScore: {score}\n")
            results_file.write('\n')

        return results

    def find_min_window_size(self, positions, high_IDF_terms_in_query, max_window_size):
        min_size = float("inf") 
        # If the document does not contain all of the high IDF terms in the query, return inf
        if not all(term in positions.keys() for term in high_IDF_terms_in_query):
            return min_size

        # positions = {term1: [pos1,pos2,...]), term2: [pos1,pos2,...]}
        all_positions = sorted(set().union(*(positions.values()))) # get all the positions of the terms in the document and sort them
        for index in range(len(all_positions)): # for each position
            start_pos = all_positions[index] 
            for end_pos in all_positions[index:]: # for each position after the start position
                if end_pos - start_pos + 1 > max_window_size or end_pos - start_pos + 1 > min_size : # if the window is bigger than the max window size or bigger than the current min window size, discard the window and all the windows after it
                    break
                possible_window = True 
                for term in positions.keys(): # for each term in the document
                    if not any( start_pos <= pos <= end_pos for pos in positions[term]): # if the term is not in the window, the window is not possible 
                        possible_window = False
                        break
                if possible_window:
                    min_size = min(min_size, end_pos - start_pos + 1) 
        return min_size      
        
class TFIDFRanking(BaseSearcher):

    def __init__(self, smart, **kwargs) -> None:
        super().__init__(**kwargs)
        self.smart = smart
        print("init TFIDFRanking|", f"{smart=}")
        if kwargs:
            print(f"{self.__class__.__name__} also caught the following additional arguments {kwargs}")

    def search_mwb(self, index, query_tokens, top_k, B):
        # index must be compatible with tfidf
        query_length = 0 # query length for normalization
        for token in query_tokens: # for each token in the query
            idf, docs = index.read_idf_documents(token) # get the idf and the documents
            query_tokens[token] = ((1 + math.log10(query_tokens[token][0])) * idf, docs) # update the query token with the term weight (idf * tf) and documents
            query_length += query_tokens[token][0] ** 2 # update the query length
        query_length = query_length ** 0.5
        # query_tokens has the following structure: {token: (normalized_term_weight_in_the_query, ["doc_id1:normalized_term_weight_in_the_docid1", "doc_id2:normalized_term_weight_in_the_docid2", ...])}

        # so, since query_tokens[token][1] is a list of strings, we need to split each element by ":" to get both the doc_id and the normalized_term_weight_in_the_doc
        doc_scores = {}
        high_idfs = {} # dict to store the top high idf tokens as keys and (idf, [(doc_id1, pos1,pos2,...),...]) as values
        for token in query_tokens: # for each token in the query
            idf, docs = query_tokens[token]
            high_idfs[token] = (idf, []) # save the idf and the positions of the token in the documents with respective doc_id
            for doc in docs: # for each document in the list of documents
                doc_id, doc_weight, pos = doc.split(":") # split the doc_id and the normalized_term_weight_in_the_doc
                doc_id, doc_weight = int(doc_id), idf / query_length * float(doc_weight) # convert the doc_id to int and calculate prod = normalized_term_weight_in_the_query * normalized_term_weight_in_the_doc 
                high_idfs[token][1].append((doc_id, pos))
                if doc_id in doc_scores: # if the doc_id is already in the doc_scores dict
                    doc_scores[doc_id] += doc_weight # update the score
                else: # if the doc_id is not in the doc_scores dict
                    doc_scores[doc_id] = doc_weight # add the doc_id to the dict with the score

        high_idfs = dict(sorted(high_idfs.items(), key=lambda x: x[1][0], reverse=True)[:int(8 + math.log( len(query_tokens) , 2 ))]) # get the top high idf tokens

        positions = {} # { doc_id1: {term1: [pos1,pos2,...]}, ..} , positions of the high idf terms in the documents 
        for token in high_idfs:
            for doc_id, pos in high_idfs[token][1]:
                if doc_id in positions:
                    positions[doc_id][token] = [int(p) for p in pos.split(",")]
                else:
                    positions[doc_id] = {token: [int(p) for p in pos.split(",")]}

        n_distinct_query_terms = len(high_idfs.keys())
        # for each document, calculate the min window size of the high idf terms, and boost the score of the document 
        for doc_id in positions:
            min_window_size = self.find_min_window_size(positions[doc_id], high_idfs.keys(), 2 * n_distinct_query_terms + math.log(n_distinct_query_terms, 2))
            if min_window_size != float("inf"):
                boost = B * ( 1 -  ( (min_window_size - n_distinct_query_terms) / min_window_size ) )
                #boost = B * n_distinct_query_terms / min_window_size # another approach with worse results
                doc_scores[doc_id] *= boost

        #sort doc scores by value and return the top k
        return dict(sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k])  

    def search(self, index, query_tokens, top_k):
        # index must be compatible with tfidf
        query_length = 0 # query length for normalization
        for token in query_tokens: # for each token in the query
            idf, docs = index.read_idf_documents(token) # get the idf and the documents
            query_tokens[token] = ((1 + math.log10(query_tokens[token][0])) * idf, docs) # update the query token with the term weight (idf * tf) and documents
            query_length += query_tokens[token][0] ** 2 # update the query length
        query_length = query_length ** 0.5
        # query_tokens has the following structure: {token: (normalized_term_weight_in_the_query, ["doc_id1:normalized_term_weight_in_the_docid1", "doc_id2:normalized_term_weight_in_the_docid2", ...])}

        # so, since query_tokens[token][1] is a list of strings, we need to split each element by ":" to get both the doc_id and the normalized_term_weight_in_the_doc
        doc_scores = {}
        for token in query_tokens: # for each token in the query
            idf, docs = query_tokens[token]
            for doc in docs: # for each document in the list of documents
                doc_id, doc_weight, pos = doc.split(":") # split the doc_id and the normalized_term_weight_in_the_doc
                doc_id, doc_weight = int(doc_id), idf / query_length * float(doc_weight) # convert the doc_id to int and calculate prod = normalized_term_weight_in_the_query * normalized_term_weight_in_the_doc 
                if doc_id in doc_scores: # if the doc_id is already in the doc_scores dict
                    doc_scores[doc_id] += doc_weight # update the score
                else: # if the doc_id is not in the doc_scores dict
                    doc_scores[doc_id] = doc_weight # add the doc_id to the dict with the score

        #sort doc scores by value and return the top k
        return dict(sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k])       

class BM25Ranking(BaseSearcher):

    def __init__(self, k1, b, **kwargs) -> None:
        super().__init__(**kwargs)
        self.k1 = k1
        self.b = b
        print("init BM25Ranking|", f"{k1=}", f"{b=}")
        if kwargs:
            print(f"{self.__class__.__name__} also caught the following additional arguments {kwargs}")

    def search_mwb(self, index, query_tokens, top_k, B):
        # index must be compatible with bm25
        doc_scores = {} # dict that will contain the doc_id and the score
        # query_tokens has the following structure: {token: (tf, "pos1,pos2,pos3,...")}
        query_tokens = query_tokens.keys() # get the query tokens
        high_idfs = {} # dict to store the top high idf tokens as keys and (idf, [(doc_id1, pos1,pos2,...),...]) as values
        for token in query_tokens: # for each token in the query
            idf, docs = index.read_idf_documents(token) # get the idf and the documents
            high_idfs[token] = (idf, []) # save the idf and the positions of the token in the documents with respective doc_id
            for doc in docs: # for each document in the list of documents
                doc_id, doc_weight, pos = doc.split(":") # split the doc_id and the normalized_term_weight_in_the_doc
                doc_id, doc_weight = int(doc_id), float(doc_weight) # convert the doc_id to int and the doc_weight to float
                high_idfs[token][1].append((doc_id, pos))
                if doc_id in doc_scores: # if the doc_id is already in the doc_scores dict
                    doc_scores[doc_id] += idf * doc_weight  # update the score
                else:
                    doc_scores[doc_id] = idf * doc_weight # add the doc_id to the dict with the score
        
        high_idfs = dict(sorted(high_idfs.items(), key=lambda x: x[1][0], reverse=True)[:int(8 + math.log( len(query_tokens) , 2 ))]) # get the top high idf tokens

        positions = {} # { doc_id1: {term1: [pos1,pos2,...]}, ..}, positions of the high idf terms in the documents 
        for token in high_idfs: 
            for doc_id, pos in high_idfs[token][1]:
                if doc_id in positions:
                    positions[doc_id][token] = [int(p) for p in pos.split(",")]
                else:
                    positions[doc_id] = {token: [int(p) for p in pos.split(",")]}
        
        n_distinct_query_terms = len(high_idfs.keys())
        # for each document, calculate the min window size of the high idf terms, and boost the score of the document 
        for doc_id in positions:
            min_window_size = self.find_min_window_size(positions[doc_id], high_idfs.keys(), 2 * n_distinct_query_terms + math.log(n_distinct_query_terms, 2))
            if min_window_size != float("inf"):
                #boost = B * n_distinct_query_terms / min_window_size # another approach with worse results
                boost = B * ( 1 -  ( (min_window_size - n_distinct_query_terms) / min_window_size ) )
                doc_scores[doc_id] *= boost

        #sort doc scores by value and return the top k
        return dict(sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k])        

    def search(self, index, query_tokens, top_k):
        # index must be compatible with bm25
        doc_scores = {} # dict that will contain the doc_id and the score
        # query_tokens has the following structure: {token: (tf, "pos1,pos2,pos3,...")}
        query_tokens = query_tokens.keys() 
        for token in query_tokens: # for each token in the query
            idf, docs = index.read_idf_documents(token) # get the idf and the documents
            for doc in docs: # for each document in the list of documents
                doc_id, doc_weight, pos = doc.split(":") # split the doc_id and the normalized_term_weight_in_the_doc
                doc_id, doc_weight = int(doc_id), float(doc_weight) # convert the doc_id to int and the doc_weight to float
                if doc_id in doc_scores: # if the doc_id is already in the doc_scores dict
                    doc_scores[doc_id] += idf * doc_weight  # update the score
                else:
                    doc_scores[doc_id] = idf * doc_weight # add the doc_id to the dict with the score

        #sort doc scores by value and return the top k
        return dict(sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k])        