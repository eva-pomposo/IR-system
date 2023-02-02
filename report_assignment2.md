# Brief explanation
This assignment is the continuation of the previous one, it was developed in the same source code repository. The assignment1 report can be accessed here: https://github.com/detiuaveiro/ri2022-assignment1-98470_98513/blob/master/report_assignment1.md

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

## New indexer CLI arguments (can be consulted in main.py).
### Some arguments were added to run the indexer in this assignment (the other ones were inherited from assignment1 and can be consulted in its report):
```

### It's important to notice that every new argument is optional. If no argument is passed, the default values will be used.
### These are the Indexer Parser Settings related to how the inverted index is built and stored, regarding the ranking schema that is being used:
```
```
--indexer.tfidf.cache_in_disk: The index will cache all intermediate values in order to speed up the TFIDF computations. (default: False, simply pass it to enable)

--indexer.tfidf.smart: The smart notation to be used if --indexer.tfidf.cache_in_disk is enabled. (default: lnc.ltc, can also use ltc.ltc, which was the other schema that we implemented)

--indexer.bm25.cache_in_disk: The index will cache all intermediate values in order to speed up the BM25 computations. (default: False, simply pass it to enable)

--indexer.bm25.k1: The k1 parameter to be used if --indexer.bm25.cache_in_disk is enabled. (default: 1.2)

--indexer.bm25.b: The b parameter to be used if --indexer.bm25.cache_in_disk is enabled. (default: 0.75)
```

### Example of different CLI instructions to run the indexer, for each schema:
```
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinyLncLtc --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.tfidf.smart lnc.ltc --indexer.tfidf.cache_in_disk

python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinyLtcLtc --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.tfidf.smart ltc.ltc --indexer.tfidf.cache_in_disk

python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinyBm25  --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.bm25.cache_in_disk 
```

## Searcher CLI arguments (can be consulted in main.py).
### These are the mandatory Searcher Parser arguments:
```
index_folder: Path to the folder where all the index related files will be loaded.

path_to_questions: Path to the file that contains the question to be processed, one per line.

output_file: File where the found documents will be returned for each question.
```

### This is the only optional argument that can be passed to the Searcher Parser:
```
--top_k: Number of documents to be returned for each question. (default: 1000)
```

### These are the Searcher Mode Parser Settings that define how the search will work, regarding the ranking schema that is being used:
### It is mandatory to pass a ranking schema, either ranking.tfidf or ranking.bm25.
```
-> ranking.tfidf - Uses the TFIDF as the searching method 

--ranking.tfidf.class: Python class that will be used to compute the TF-IDF score. (default: TFIDFRanking, which is the implemented one) 

--ranking.tfidf.smart: The smart notation to be used if --ranking.tfidf.class is TFIDFRanking. (default: lnc.ltc, can also use ltc.ltc, which was the other schema that we implemented)

-> ranking.bm25 - Uses the BM25 as the searching method

--ranking.bm25.class: Python class that will be used to compute the BM25 score. (default: BM25Ranking, which is the implemented one)

--ranking.bm25.k1: k1 value used in the BM25 algorithm. (default: 1.2)

--ranking.bm25.b: b value used in the BM25 algorithm. (default: 0.75)
```

### Example of different CLI instructions to run the searcher in batch_search mode, for each schema:
```
python3 main.py searcher results/pubmedSPIMIindexTinyLncLtc/mergedFiles questions/questions1.txt paginator_tfidf_lnc_ltc.txt ranking.tfidf

python3 main.py searcher results/pubmedSPIMIindexTinyLtcLtc/mergedFiles questions/questions1.txt paginator_tfidf_ltc_ltc.txt ranking.tfidf

python3 main.py searcher results/pubmedSPIMIindexTinyBm25/mergedFiles questions/questions1.txt paginator_bm25.txt ranking.bm25
```

### Example of different CLI instructions to run the searcher in interactive_search mode, for each schema:
### Since the path_to_questions is a mandatory argument, we must pass an unexistant path to it, so that we can try the interactive mode.
```
python3 main.py searcher results/pubmedSPIMIindexTinyLncLtc/mergedFiles questions/no_questions_file.txt paginator_tfidf_lnc_ltc.txt ranking.tfidf

python3 main.py searcher results/pubmedSPIMIindexTinyLtcLtc/mergedFiles questions/no_questions_file.txt paginator_tfidf_ltc_ltc.txt ranking.tfidf

python3 main.py searcher results/pubmedSPIMIindexTinyBm25/mergedFiles questions/no_questions_file.txt paginator_bm25.txt ranking.bm25
```

# Statistics

## pubmed_2022_tiny.jsonl.gz
|| 1st try | 2nd try | 3rd try |
|---|---|---|---|
| Ranking                                            | tf-idf (schema lnc.ltc)    | tf-idf (schema ltc.ltc)    | Okapi BM25                 |
| Minimum length filter                              | yes (size 3)               | yes (size 3)               | yes (size 3)               | 
| Stopword filter                                    | yes                        | yes                        | yes                        | 
| Porter stemmer filter                              | yes                        | yes                        | yes                        | 
| Posting threshold                                  | 80000                      | 80000                      | 80000                      | 
| Total indexing time                                | 307.3968267440796 seconds (5 min 7 sec) | 336.63906502723694 seconds (5 min 36 sec) | 329.7334358692169 seconds (5 min 29 sec) | 
| Merging time (last SPIMI step)                     | 15.027347803115845 seconds | 38.56540775299072 seconds  | 31.711694717407227 seconds | 
| Number of temporary index segments written to disk | 128                        | 128                        | 128                        | 
| Total index size on disk                           | 300746558 bytes            | 303976463 bytes            | 290425540 bytes            | 
| Vocabulary size (number of terms)                  | 379588                     | 379588                     | 379588                     | 

## pubmed_2022_small.jsonl.gz

|| 1st try | 2nd try | 3rd try |
|---|---|---|---|
| Ranking                                            | tf-idf (schema lnc.ltc)                  | tf-idf (schema ltc.ltc)                    | Okapi BM25                               |
| Minimum length filter                              | yes (size 3)                             | yes (size 3)                               | yes (size 3)                             |
| Stopword filter                                    | yes                                      | yes                                        | yes                                      |
| Porter stemmer filter                              | yes                                      | yes                                        | yes                                      |
| Posting threshold                                  | 540000                                   | 540000                                     | 540000                                   | 
| Total indexing time                                | 3217.70410490036 seconds (53 min 37 sec) | 3438.6435379981995 seconds (57 min 18 sec) | 3500.249306678772 seconds (58 min 20 sec)|
| Merging time (last SPIMI step)                     | 171.57684540748596 seconds (2 min 51 sec)| 423.66275238990784 seconds (7 min 3 sec)   | 386.90268421173096 seconds (6 min 26 sec)|
| Number of temporary index segments written to disk | 196                                      | 196                                        | 196                                      |
| Total index size on disk                           | 3072773075 bytes                         | 3179458534 bytes                           | 2963481183 bytes                         |
| Vocabulary size (number of terms)                  | 1842238                                  | 1842238                                    | 1842238                                  |

# Analysis of the query results
There is an example file in the questions folder, questions1.txt, that contains the questions that we can pass to the searcher. In the root folder of the repository we can find the files paginator_bm25.txt, paginator_tfidf_lnc_ltc.txt and paginator_tfidf_ltc_ltc.txt, that are the results of the queries in the questions1.txt file for the BM25, tf-idf lnc.ltc and tf-idf ltc.ltc approaches, respectively.

# Authors

| NMec | Name | Github |
|--:|---|---|
| 98513 | **Eva Bartolomeu** | [eva-pomposo](https://github.com/eva-pomposo) |
| 98470 | **Artur Romão** | [artur-romao](https://github.com/artur-romao) |
