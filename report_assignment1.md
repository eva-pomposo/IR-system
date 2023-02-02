# Instructions
## How to run

### Start by installing the requirements, creating a virtual environment for that:
```
cd ri2022-assignment1-98470_98513
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Indexer CLI arguments (can be consulted in main.py)
### These are the mandatory Indexer Parser arguments:
```
indexer: The indexer class, can also serve has a helper.

path_to_collection: Name of the folder or file that holds the document collection to be indexed.

index_output_folder: Name of the folder where all the index related files will be stored.
```
### Now regarding the optional arguments.
### These are the Indexer Parser Settings related to how the inverted index is built and stored:
```
--indexer.class: The class passed for the inverted indexer. By default is SPIMIIndexer.

--indexer.posting_threshold: Maximum number of postings that each index should hold.

--indexer.memory_threshold: Maximum limit of RAM that the program (index) should consume.
```

### These are the Indexer document processing settings, related to how the documents should be loaded and processed to tokens.
```
--reader.class: Type of reader to be used to process the input document collection. (default=PubMedReader).

--tk.class: Type of tokenizer to be used to process the loaded document. (default=PubMedTokenizer).

--tk.minL: Minimum token length. The absence means that will not be used (default=None).

--tk.stopwords_path: Path to the file that holds the stopwords. The absence means that will not be used (default=None).

--tk.stemmer: Type of stemmer to be used. The absence means that will not be used (default=None).
```
### Example of CLI instruction to run the project:
```
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindex --tk.minL 2 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 540000
```

# Code Structure

## Class Reader:
* Class responsible for opening the compressed json data file and iterating over the documents (one per line) and returning their respective content.
* pmid was considered as document identifier.
* title and abstract were considered as the content.
* Only these 3 json objects were considered for this assignment.
* Since the read() method is called line by line (document by document), the return of the method is a tuple in the following format: (docID, title + " " + abstract).
* The docID is returned as an integer to save memory (a string would fill way more memory)
## Class Tokenizer:
* Class responsible for processing the content received from the reader and create the tokens for posterior indexation.
* The method tokenize() is responsible for calling the methods that will proccess the result of the reader: create_tokens() and filter_stopw_and_stemming().
* The method create_tokens() receives the tuple from reader and, for each pmid, creates the tokens bearing some rules: only alphanumeric tokens are considered, the length of the token should be greater or equal than self.minL and the tokens should all be in lower case. The tokens can also have hyphens in between words, but never in the beginning or the end. The return of this method is a list containing the tokens for that document.
* The method filter_stopw_and_stemming() receives the list from create_tokens() and filters it using a list of stopwords and a Porter Stemmer. It has in consideration that the user might pass only the stopwords file path, only the stemmer, both or none. The return is now a list of terms (tokens fully proccessed) for each document.
* The stopwords file that we're using can be accessed here: https://gist.github.com/larsyencken/1440509
## Class Indexer:
* Class from which SPIMIIndexer is inherited.
* SPIMIIndexer is responsible to build our index.
* The most important methods in this class are build_index(), that creates multiple files containing the terms and the docIDs of the files in which they occur and merge_files(), which merge the files created in build_index() in other files by alphabetical order. These two methods also take advantage of variables and methods defined in the class InvertedIndex which is inherited from BaseIndex class.
* The method build_index() calls the read() method from the Reader Class until there are lines from the json file to read. During that proccess, the content is tokenized and an in-memory dictionary from our InvertedIndex, tokensOccurrences, is updated with the terms and a list of their respective occurrences {term: [docID1 docID2 docID3...]}. Then, the algorithm checks if the number of posts (sum of all the lengths of the occurrences lists) is greater or equal than the argument posting_threshold passed in the CLI, if so, the in-memory dictionary is wrote to a file, a new file is created and the dictionary is cleared. The proccess is repeated until we end the reading of the json file.
* Each line of an unmerged file follows this format: term docID1 docID2 docID3, ... and the whole file is written alphabetically and with sorted docIDs.
* After building up every unmerged file, there is now time to merge them all, that's when our merge_files() method is called. This method follows a min heap approach. We start by creating a list in which length = number of unmerged files. For each index of that list, it will read a line of one of the unmerged files (i.e: for index 0, it will read a line of unmergedFile1, for index 1, a line of unmergedFile2 and so on...). Then, thanks to method min(), it will select the line that comes first alphabetically, sort the occurrences and write it in the merged_file, this is the mean heap part of the algorithm. Just like in build_index(), this method checks if the written posts exceed the posting_threshold and if so, closes the merged file and creates a new one, repeating the process.

# Statistics

## pubmed_2022_tiny.jsonl.gz
|| 1st try | 2nd try | 3rd try | 4th try ||
|---|---|---|---|---|---|
| Minimum length filter                              | yes (size 3)               | yes (size 2)               | yes (size 2)               | yes (size 3)              
| Stopword filter                                    | yes                        | yes                        | yes                        | yes                       
| Porter stemmer filter                              | yes                        | yes                        | yes                        | yes                       
| Posting threshold                                  | 50000                      | 80000                      | 80000                      | 80000                     
| Total indexing time                                | 203.59035921096802 seconds | 253.54508543014526 seconds | 245.06186628341675 seconds | 188.51956701278687 seconds
| Merging time (last SPIMI step)                     | 18.636372566223145 seconds | 14.853941679000854 seconds | 15.817283391952515 seconds | 13.050742864608765 seconds
| Number of temporary index segments written to disk | 205                        | 135                        | 135                        | 128                       
| Total index size on disk                           | 94232630 bytes             | 98978803 bytes             | 98978803 bytes             | 94232714 bytes            
| Vocabulary size (number of terms)                  | 379588                     | 380184                     | 380184                     | 379588                    

## pubmed_2022_small.jsonl.gz

|| 1st try |
|---|---|
| Minimum length filter                              | yes (size 3)              |
| Stopword filter                                    | yes                       |
| Porter stemmer filter                              | yes                       |
| Posting threshold                                  | 540000                    | 
| Total indexing time                                | 2134.297646999359 seconds (35 min 34 sec)|
| Merging time (last SPIMI step)                     | 156.3487274646759 seconds (2 min 36 sec)|
| Number of temporary index segments written to disk | 196                       |
| Total index size on disk                           | 954767876 bytes           |
| Vocabulary size (number of terms)                  | 1842238                   |

## pubmed_2022_medium.jsonl.gz

|| 1st try |
|---|---|
| Minimum length filter                              | yes (size 3)             | 
| Stopword filter                                    | yes                      | 
| Porter stemmer filter                              | yes                      | 
| Posting threshold                                  | 540000                   | 
| Total indexing time                                | 7937.725738286972 seconds (2h 12min 17s) | 
| Merging time (last SPIMI step)                     | 1250.789216518402 seconds (20min 50s) | 
| Number of temporary index segments written to disk | 654 | 
| Total index size on disk                           | 3161228186 bytes | 
| Vocabulary size (number of terms)                  | 4146673 | 

## pubmed_2022_large.jsonl.gz

To run the program with this gzip file we had to increase the maximum number of open files a process can have. To do this, simply run the following command on the computer that will run the program:

```
ulimit -n 2000
```

This command will change the maximum number of open files in a process to 2000. This condition is necessary because in the merge part all the unmerged files will be open (which exceeds the default value).

|| 1st try |
|---|---|
| Minimum length filter                              | yes (size 3)             |
| Stopword filter                                    | yes                      |
| Porter stemmer filter                              | yes                      |
| Posting threshold                                  | 540000                   | 
| Total indexing time                                | 15261 seconds (4h 14min 21s)     |
| Merging time (last SPIMI step)                     | 3237.220776796341 seconds (53 min 57s) |
| Number of temporary index segments written to disk | 1443                     |
| Total index size on disk                           | 6943443026 bytes         |
| Vocabulary size (number of terms)                  | 7201015                  |


# Authors

| NMec | Name | Github |
|--:|---|---|
| 98513 | **Eva Bartolomeu** | [eva-pomposo](https://github.com/eva-pomposo) |
| 98470 | **Artur Romão** | [artur-romao](https://github.com/artur-romao) |
