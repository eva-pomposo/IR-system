import json
import linecache
import math
import os
import time
from nltk.stem import PorterStemmer

"""
Base template created by: Tiago Almeida & Sérgio Matos
Authors: 

Indexer module

Holds the code/logic addressing the Indexer class
and the index managment.

"""

from utils import dynamically_init_class


def dynamically_init_indexer(**kwargs):
    """Dynamically initializes a Indexer object from this
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


class Indexer:
    """
    Top-level Indexer class
    
    This loosly defines a class over the concept of 
    an index.

    """
    
    def __init__(self, 
                 index_instance,
                 **kwargs):
        super().__init__()
        self._index = index_instance
    
    def get_index(self):
        return self._index
    
    def build_index(self, reader, tokenizer, index_output_folder):
        """
        Holds the logic for the indexing algorithm.
        
        This method should be implemented by more specific sub-classes
        
        Parameters
        ----------
        reader : Reader
            a reader object that knows how to read the collection
        tokenizer: Tokenizer
            a tokenizer object that knows how to convert text into
            tokens
        index_output_folder: str
            the folder where the resulting index or indexes should
            be stored, with some additional information.
            
        """
        raise NotImplementedError()
    

class SPIMIIndexer(Indexer):
    """
    The SPIMIIndexer represents an indexer that
    holds the logic to build an index according to the
    spimi algorithm.

    """
    def __init__(self, 
                 posting_threshold, 
                 memory_threshold, 
                 **kwargs):
        # lets suppose that the SPIMIIindex uses the inverted index, so
        # it initializes this type of index
        super().__init__(InvertedIndex(), **kwargs)
        self.memory_threshold  = memory_threshold if memory_threshold else 60 # Initialize the memory_threshold and define default value
        self.posting_threshold = posting_threshold if posting_threshold else 80000 # Initialize the posting_threshold and define default value
        print("init SPIMIIndexer|", f"{posting_threshold=}, {memory_threshold=}")
        if kwargs:
            print(f"{self.__class__.__name__} also caught the following additional arguments {kwargs}")
            self.args_dict = kwargs
        
    def build_index(self, reader, tokenizer, index_output_folder):
        print("Indexing some documents...")

        # Create the results folders if they don't exist already
        if not os.path.isdir("results"): 
            os.mkdir("results")
        if not os.path.isdir("results/" + index_output_folder):
            os.mkdir("results/" + index_output_folder)
            os.mkdir("results/" + index_output_folder + "/mergedFiles")
        else:
            [os.remove("".join(["results/", index_output_folder, "/mergedFiles/", file])) for file in os.listdir("".join(["results/", index_output_folder, "/mergedFiles"]))]
        os.mkdir("".join(["results/", index_output_folder, "/unmergedFiles"]))
        
        # Store the tokenizer arguments in a file
        with open("results/" + index_output_folder + "/tokenizer_metadata.txt", "w") as f:
            if tokenizer.stopwords_path: # If the tokenizer has stopwords
                if tokenizer.stemmer and (type(tokenizer.stemmer) is PorterStemmer): # If the tokenizer has a stemmer and it is a PorterStemmer
                    f.write("{\"class\": \"%s\",  \"minL\": %d, \"stopwords_path\": \"%s\", \"stemmer\": \"potterNLTK\"}" % (tokenizer.__class__.__name__, tokenizer.minL, tokenizer.stopwords_path))
                else: # If the tokenizer hasn't a stemmer or it is not a PorterStemmer
                    f.write("{\"class\": \"%s\", \"minL\": %d, \"stopwords_path\": \"%s\", \"stemmer\": null}" % (tokenizer.__class__.__name__, tokenizer.minL, tokenizer.stopwords_path))
            elif tokenizer.stemmer and (type(tokenizer.stemmer) is PorterStemmer): # If the tokenizer hasn't stopwords but has a stemmer and it is a PorterStemmer
                f.write("{\"class\": \"%s\", \"minL\": %d, \"stopwords_path\": null, \"stemmer\": \"potterNLTK\"}" % (tokenizer.__class__.__name__, tokenizer.minL))
            else: # If the tokenizer hasn't stopwords and hasn't a stemmer or it is not a PorterStemmer
                f.write("{\"class\": \"%s\", \"minL\": %d, \"stopwords_path\": null, \"stemmer\": null}" % (tokenizer.__class__.__name__, tokenizer.minL))

        self._index.total_indexing_time = time.time() # Start counting the indexing_time
        pmid, content = reader.read() # Read document
        while pmid and content: # While there are lines to read
            terms = tokenizer.tokenize(content) # Tokenize the content get the dictionary of terms and a tuple (term frequency, positions) as values
            if not self.args_dict["bm25"]["cache_in_disk"] and self.args_dict["tfidf"]["smart"] == "lnc.ltc": # If the cache_in_disk of the bm25 is false and the smart of the tfidf is lnc.ltc
                doc_length = 0 # Initialize the document length
                for term, tf_pos in terms.items(): # For each term in the document
                    terms[term] = 1 + math.log10(tf_pos[0]), tf_pos[1] # Calculate the log frequency weight of the term, that is the weight of the term in the document, in schema lnc.ltc
                    doc_length += terms[term][0]**2 # Calculate the document length
                doc_length = math.sqrt(doc_length) 

                terms = {term: (tf_pos[0]/doc_length, tf_pos[1]) for term, tf_pos in terms.items()} # dictionary with the terms as keys and a tuple (normalized term weight, positions) as values
            
            # SPIMI-Invert
            if self._index.count_posts + len(terms) >= self.posting_threshold: # If the number of in memory posts + the ones that we will add to the index exceed the posting_threshold, write to disk
                self._index.write_block_to_disk(index_output_folder)
            
            if self.args_dict["bm25"]["cache_in_disk"]: # If the cache_in_disk of the bm25 is true
                doc_length = sum([tf_pos[0] for tf_pos in terms.values()]) # Calculate the document length                
                self._index.avg_length += doc_length # Increment the average length of the documents
                [self._index.add_term(term, pmid, tf_pos, doc_length) for term, tf_pos in terms.items()] # Add each term to the in memory index
            else:
                [self._index.add_term(term, pmid, tf_pos) for term, tf_pos in terms.items()] # Add each term to the in memory index
            self._index.num_of_docs += 1 # Increment the number of documents

            pmid, content = reader.read() # Read document
        if self.args_dict["bm25"]["cache_in_disk"]: # If the cache_in_disk of the bm25 is true
            self._index.avg_length /= self._index.num_of_docs # Calculate the average length of the documents
        self._index.merging_time = time.time() # Start counting the merging_time
        self.merge_files(index_output_folder, self._index.get_termsOccurrences()) # Start the merge
        self._index.merging_time = time.time() - self._index.merging_time # Calculate the merging_time
        self._index.total_indexing_time = time.time() - self._index.total_indexing_time # Calculate the indexing_time
        # Calculate the total_index_size below
        self._index.total_index_size = sum([os.path.getsize("results/" + index_output_folder + "/mergedFiles/" + file) for file in os.listdir("results/" + index_output_folder + "/mergedFiles")])

    def merge_files(self, index_output_folder, inverted_index):
        # Sort every unmerged file by their creation time
        unmerged_files_names = sorted(os.listdir("results/" +  index_output_folder + "/unmergedFiles"), key=lambda x: os.stat("results/" +  index_output_folder + "/unmergedFiles/" + x))
        unmerged_files = [open("results/" +  index_output_folder + "/unmergedFiles/" + filename) for filename in unmerged_files_names] # Open every unmerged file
        current_lines = [unmerged_file.readline()[:-1] for unmerged_file in unmerged_files] # Store the first line of each file in a list, except the last character (\n)
        if inverted_index: # If the {term: "doc_id:tf:pos1,pos2,..."} dictionary is not empty
            # Append the first term alphabetically and its respective posting list from in memory dictionary
            current_lines.append(min(inverted_index.keys()) + " " + inverted_index[min(inverted_index.keys())])

        last_merged_file_term, last_postings, count_merge_posts, count_merged_files, last_term = "", [], 0, 1, ""

        first_index = current_lines.index(min(current_lines)) # Get the index of the first line alphabetically
        first_line = current_lines[first_index] # Get the first line alphabetically
        first_term = first_line.split()[0] # Get the first term
        merged_file = open("results/" +  index_output_folder + "/mergedFiles/" + first_term + ".txt", 'wt') # Create the first merged file

        while current_lines: # While there are lines to merge
            current_index = current_lines.index(min(current_lines)) # The current_index will correspond to the index of the first term alphabetically 
            current_line = current_lines[current_index] # This variable stores the term and its associated docIDs and occurences number as a whole string (ie: term doc1:tf doc2:tf doc3:tf...)
            current_term = current_line.split()[0] # Get the first word of current_line which corresponds to the term
            current_postings = current_line.split()[1:] # Get the posts of current_line

            if current_term != last_merged_file_term: # If the current_term changes
                if last_merged_file_term != "": # If it's not the first time of while
                    # If the already written posts + the ones that will be written exceed the posting_threshold: close the file and create another one, also reset the count_merge_posts
                    if count_merge_posts + len(last_postings) >= self.posting_threshold:
                        old_file_name = os.path.splitext(merged_file.name)[0] # Get the name of the old file without extension
                        os.rename("".join([old_file_name, ".txt"]), "".join([old_file_name, "  ", last_term, ".txt"])) # Rename the old file appending the last term of the file
                        merged_file.close()
                        count_merged_files += 1
                        merged_file = open("".join(["results/", index_output_folder, "/mergedFiles/", last_merged_file_term, ".txt"]), 'wt')
                        count_merge_posts = 0
                    # Else, write only both the last term and its sorted posts to the merged file
                    last_postings = sorted(last_postings, key=lambda x: int(x.split(":")[0]))
                    idf = math.log10(self._index.num_of_docs / len(last_postings)) # Calculate the idf of the term
                    if not self.args_dict["bm25"]["cache_in_disk"] and self.args_dict["tfidf"]["smart"] == "ltc.ltc": # If the cache_in_disk of the bm25 is false and the smart of the tfidf is ltc.ltc
                        update_last_postings = [] # Create a list to store the updated posts
                        doc_length = 0 # Initialize the doc_length
                        for post in last_postings: # For each post
                            doc_id, tf, pos = post.split(":") # Get the doc_id and the tf
                            tf = 1 + math.log10(int(tf)) # Calculate the tf_log
                            update_last_postings.append(doc_id + ":" + str(float(tf) * idf) + ":" + pos) # Append the doc_id and the tf_log * idf to the list, that is the weight of the term in the document, in schema ltc.ltc
                            doc_length += (float(tf) * idf) ** 2 # Calculate the doc_length
                        last_postings = update_last_postings # Update the last_postings
                        doc_length = math.sqrt(doc_length)
                        last_postings = [post.split(":")[0] + ":" + str(float(post.split(":")[1]) / doc_length) + ":" + post.split(":")[2] for post in last_postings] # Normalize 
                    elif self.args_dict["bm25"]["cache_in_disk"]: # If the cache_in_disk of the bm25 is true
                        #idf = math.log(1 + (self._index.num_of_docs - len(last_postings) + 0.5) / (len(last_postings) + 0.5))
                        # Calculate the weight of the term in the document, in schema bm25
                        last_postings = [doc_id + ":" + str( ( float(tf_raw) * (self.args_dict["bm25"]["k1"] + 1) ) / ( float(tf_raw) + self.args_dict["bm25"]["k1"] * (1 - self.args_dict["bm25"]["b"] + self.args_dict["bm25"]["b"] * (int(doc_length)/self._index.avg_length)) )) + ":" + pos for doc_id, tf_raw, doc_length, pos in [post.split(":") for post in last_postings]]
                    merged_file.write("%s:%f %s" % (last_merged_file_term, idf, " ".join(last_postings) )) if count_merge_posts == 0 else merged_file.write("\n%s:%f %s" % (last_merged_file_term, idf, " ".join(last_postings))) # Write the last term and its sorted posts to the merged file with idf at the beginning of the line (ie: term:idf doc1:w:pos doc2:w:pos doc3:w:pos...)
                    self._index.vocabulary_size += 1 # Increment the vocabulary size
                    count_merge_posts += len(last_postings) # Increment the number of posts for that merged file
                last_term = last_merged_file_term
                last_merged_file_term = current_term # Update the variable last_merged_file_term with the new term
                last_postings = current_postings # Update the variable last_postings with the new postings
            else: # If current_term = last_merged_file_term, let's add to last_postings the current_postings
                last_postings += current_postings

            # If there are still terms in memory AND if the index of the term we just wrote to the merge is the last one (that means the term we wrote to the merge file is in memory)
            if inverted_index and current_index == len(current_lines) - 1:
                inverted_index.pop(min(inverted_index.keys())) # Remove term from memory
                if inverted_index: # Verify if there are still terms in memory
                    # If there are, replace the term that we just wrote to the merge for the first term in memory (following the alphabetic order)
                    current_lines[current_index] = " ".join([min(inverted_index.keys()), inverted_index[min(inverted_index.keys())] ])
                else:
                    current_lines.pop(current_index) # If there are no terms in memory, remove the term we just wrote in the merge file from current_lines list
            else: # If there are no terms in memory or, in case there is, if the index of the term we just wrote in the merge file is not the last one
                current_lines[current_index] = unmerged_files[current_index].readline()[:-1] # Update the index of the just written term in the list current_lines by reading another line

                if current_lines[current_index] == "": # If the next line is empty, close the file, pop the file from the unmerged files list and pop the empty line from current_lines
                    unmerged_files[current_index].close() 
                    unmerged_files.pop(current_index)
                    current_lines.pop(current_index)

        # write both the last term and its sorted posts to the merged file
        last_postings = sorted(last_postings, key=lambda x: int(x.split(":")[0]))
        idf = math.log10(self._index.num_of_docs / len(last_postings)) # Calculate the idf of the term
        if not self.args_dict["bm25"]["cache_in_disk"] and self.args_dict["tfidf"]["smart"] == "ltc.ltc": # If the cache_in_disk of the bm25 is false and the smart of the tfidf is ltc.ltc
            update_last_postings = [] # Create a list to store the updated posts
            doc_length = 0 # Initialize the doc_length
            for post in last_postings: # For each post
                doc_id, tf, pos = post.split(":") # Get the doc_id, the tf and the positions
                tf = 1 + math.log10(int(tf)) # Calculate the tf_log
                update_last_postings.append(doc_id + ":" + str(float(tf) * idf) + ":" + pos) # Append the doc_id and the tf_log * idf to the list, that is the weight of the term in the document, in schema ltc.ltc
                doc_length += (float(tf) * idf) ** 2
            last_postings = update_last_postings # Update the last_postings
            doc_length = math.sqrt(doc_length)
            last_postings = [post.split(":")[0] + ":" + str(float(post.split(":")[1]) / doc_length) + ":" + post.split(":")[2] for post in last_postings] # Normalize 
        elif self.args_dict["bm25"]["cache_in_disk"] : # If the cache_in_disk of the bm25 is true
            #idf = math.log(1 + (self._index.num_of_docs - len(last_postings) + 0.5) / (len(last_postings) + 0.5))
            # Calculate the weight of the term in the document, in schema bm25
            last_postings = [doc_id + ":" + str( ( float(tf_raw) * (self.args_dict["bm25"]["k1"] + 1) ) / ( float(tf_raw) + self.args_dict["bm25"]["k1"] * (1 - self.args_dict["bm25"]["b"] + self.args_dict["bm25"]["b"] * (int(doc_length)/self._index.avg_length)) )) + ":" + pos for doc_id, tf_raw, doc_length, pos in [post.split(":") for post in last_postings]]
        merged_file.write("%s:%f %s" % (last_merged_file_term, idf, " ".join(last_postings))) # Write the last term and its sorted posts to the merged file with idf at the beginning of the line (ie: term:idf doc1:w doc2:w doc3:w...)
        self._index.vocabulary_size += 1 # Increment the vocabulary size
        old_file_name = os.path.splitext(merged_file.name)[0] # Get the name of the old file without extension
        os.rename("".join([old_file_name, ".txt"]), "".join([old_file_name, "  ", last_merged_file_term, ".txt"])) # Rename the old file appending the last term of the file
        merged_file.close() # Close the last merged file

        # Remove the unmerged files to save disk space
        [os.remove("".join(["results/", index_output_folder, "/unmergedFiles/", filename])) for filename in os.listdir("".join(["results/", index_output_folder, "/unmergedFiles"]))]
        os.rmdir("".join(["results/", index_output_folder, "/unmergedFiles"]))
        
class BaseIndex:
    """
    Top-level Index class
    
    This loosly defines a class over the concept of 
    an index.

    """

    def get_tokenizer_kwargs(self):
        """
        Index should store the arguments used to initialize the index as aditional metadata
        """
        if not os.path.isfile(os.path.join(self.path_to_folder, "../tokenizer_metadata.txt")): # If the file doesn't exist, return an empty dictionary
            return {}
        # Read the file tokenizer_metadata.txt and return the arguments used to initialize the tokenizer
        with open(os.path.join(self.path_to_folder, "../tokenizer_metadata.txt"), "r") as f:
            return json.loads(f.read())

    def add_term(self, term, doc_id, *args, **kwargs):
        raise NotImplementedError()
    
    def print_statistics(self):
        raise NotImplementedError()
    
    @classmethod
    def load_from_disk(cls, path_to_folder:str):
        # cls is an argument that referes to the called class, use it for initialize your index
        """
        Loads the index from disk, note that this
        the process may be complex, especially if your index
        cannot be fully loaded. Think of ways to coordinate
        this job and have a top-level abstraction that can
        represent the entire index even without being fully load
        in memory.
        
        Tip: The most important thing is to always know where your
        data is on disk and how to easily access it. Recall that the
        disk access are the slowest operation in a computation device, 
        so they should be minimized.
        
        Parameters
        ----------
        path_to_folder: str
            the folder where the index or indexes are stored.
            
        """
        if not os.path.isdir(path_to_folder): # If the path_to_folder is not a directory, raise an exception
            raise ValueError("The path_to_folder (%s) argument must be a valid directory", path_to_folder)

        baseIndex = cls() # Initialize the index
        baseIndex.path_to_folder = path_to_folder # Save the path to the folder where the index is stored
        baseIndex.merged_files = sorted(os.listdir(path_to_folder)) # Get the list of the merged files in the folder
        return baseIndex # Return the index

    def read_idf_documents(self, token): # Read the idf and the documents of a term
        file = self.binary_search_find_proper_token_merge_file(token) # Find the file where the term is stored

        if file:
            return self.binary_search_find_token_in_merge_file(token, file) # Return the idf and the documents of the term
        print('File not found')
        return 0, []
    
    # Binary search to find the line where the term is stored in the merge file
    def binary_search_find_token_in_merge_file(self, token, file):
        with open(os.path.join(self.path_to_folder, file), 'r') as f: # Open the file
            first = 1 # index of the first line
            last = len(f.readlines()) # index of the last line
            while first <= last: # While the first index is less than or equal to the last index
                mid = (first + last) // 2 # Get the middle index
                line = linecache.getline(os.path.join(self.path_to_folder, file), mid) # Get the line at the middle index
                term, idf = line.split()[0].split(':') # Get the term and the idf of the line
                if term == token: # If the term is the token we are looking for, return the idf and the documents of the term
                    return float(idf), line.split()[1:]
                elif term < token: # If the term is less than the token we are looking for, search in the left half of the file
                    first = mid + 1
                else: # If the term is greater than the token we are looking for, search in the right half of the file
                    last = mid - 1
            return 0, []

    # Binary search to find the file where the term is it possible to be stored
    def binary_search_find_proper_token_merge_file(self, token):
        low = 0 # The first index of the list
        high = len(self.merged_files) - 1 # The last index of the list
        mid = 0 # The middle index of the list

        while low <= high: # While the first index is less than or equal to the last index
            mid = (high + low) // 2 # Get the middle index of the list
            
            terms = self.merged_files[mid].split('  ') # Get the terms of the file
            
            if terms[0] <= token <= terms[1]: # If the token is between the terms of the file, return the file
                return self.merged_files[mid]
            elif token < terms[0]: # If the token is less than the first term of the file, search in the left half of the list
                high = mid - 1
            else: # If the token is greater than the second term of the file, search in the right half of the list
                low = mid + 1

        return None

class InvertedIndex(BaseIndex):
    
    # make an efficient implementation of an inverted index

    def __init__(self, **kwargs):
        self.termsOccurrences = {} # key = term, value = list containing the pmids of the docs that contain the term, the weights and positions
        self.count_posts, self.numOfDiskWrites, self.total_indexing_time, self.merging_time, self.total_index_size, self.vocabulary_size = 0, 0, 0, 0, 0, 0
        self.num_of_docs, self.avg_length = 0, 0 

    @classmethod
    def load_from_disk(cls, path_to_folder:str):
        raise NotImplementedError()
    
    def print_statistics(self):
        print("Print some stats about this index.. This should be implemented by the base classes")
        print("Total indexing time:", self.total_indexing_time)
        print("Merging time (last SPIMI step):", self.merging_time)
        print("Number of temporary index segments written to disk (before merging):", self.numOfDiskWrites)
        print("Total index size on disk:", self.total_index_size)
        print("Vocabulary size (number of terms):", self.vocabulary_size)

    def add_term(self, term, doc_id, *args, **kwargs):
        if term not in self.termsOccurrences.keys():
            if len(args) == 2: # If the cache_in_disk of the bm25 is true
                self.termsOccurrences[term] = str(doc_id) + ":" + str(args[0][0]) + ":" + str(args[1]) + ":" + args[0][1] # If the term is not in the dictionary, add it with the doc_id:tf:doc_length:pos1,pos2,... as value
            else: 
                self.termsOccurrences[term] = str(doc_id) + ":" + str(args[0][0]) + ":" + args[0][1] # If the term is not in the dictionary, add it with the doc_id:weight:pos1,pos2,... as value
        else:
            if len(args) == 2: # If the cache_in_disk of the bm25 is true
                self.termsOccurrences[term] += " " + str(doc_id) + ":" + str(args[0][0]) + ":" + str(args[1]) + ":" + args[0][1] # If the term is already in the dictionary, append the doc_id:tf:doc_length:pos1,pos2,... to its value
            else: 
                self.termsOccurrences[term] += " " + str(doc_id) + ":" + str(args[0][0]) + ":" + args[0][1] # If the term is already in the dictionary, append the doc_id:weight:pos1,pos2,... to its value
        self.count_posts += 1 # Increment the posts counter 
    
    # Method to sort both the terms and docIDs in dictionary termsOccurrences
    def sort_terms(self):
        self.termsOccurrences = dict(sorted(self.termsOccurrences.items()))
        for term, occurrences in self.termsOccurrences.items():
            self.termsOccurrences[term] = sorted(occurrences.split(" "), key=lambda x: int(x.split(":")[0]))
            self.termsOccurrences[term] = " ".join(self.termsOccurrences[term])

    def get_termsOccurrences(self):
        return self.termsOccurrences

    # Method to write the in memory dictionary to a file and free the memory
    def write_block_to_disk(self, index_output_folder):
        if self.get_termsOccurrences(): 
            self.sort_terms()
            self.numOfDiskWrites += 1
            output_file = open("".join(["results/", index_output_folder, "/unmergedFiles/unmergedFile", str(self.numOfDiskWrites), ".txt"]), 'wt')
            [output_file.write(" ".join([term, occurrences, '\n'])) for term, occurrences in self.get_termsOccurrences().items()] 
            output_file.close()
            self.termsOccurrences = {} # Free disk
            self.count_posts = 0
