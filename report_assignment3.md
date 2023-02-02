# Brief explanation
This assignment is the continuation of two previous assignments, the code of the three assignments was developed in this same source code repository. It is recommended to check the previous assignments to understand some aspects, specially how indexer and searcher work.

The assignment1 report can be accessed here: https://github.com/detiuaveiro/ri2022-assignment1-98470_98513/blob/master/report_assignment1.md

The assignment2 report can be accessed here: https://github.com/detiuaveiro/ri2022-assignment1-98470_98513/blob/master/report_assignment2.md


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

### Example of different CLI instructions to run the indexer, for each schema:
```
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinytfidf_lnc_ltc --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.tfidf.smart lnc.ltc --indexer.tfidf.cache_in_disk

python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinytfidf_ltc_ltc --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.tfidf.smart ltc.ltc --indexer.tfidf.cache_in_disk

python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinybm25  --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.bm25.cache_in_disk 
```

## New searcher CLI arguments added by us for this assignment

### These arguments can be consulted in method "add_more_options_to_searcher()" in line 42 of core.py.
### We created two new searcher CLI arguments to help in exercise 2 (both of them are optional):
```
--mwb: If this argument is passed, the Minimum Window Boost should be considered for the Document Scoring.

--B: The boost factor to be used if --mwb is passed. (default: 2)
```


### To add these arguments, we created a method add_more_options_to_searcher() in core.py, then added both mwb and B to engine_logic() args and to searcher_logic() parameters in core.py, and finally called function add_more_options_to_searcher() in main.py.


### Example of different CLI instructions to run the searcher with Minimum Window Boost, for each schema:
```
python3 main.py searcher results/pubmedSPIMIindexTinytfidf_lnc_ltc/mergedFiles questions/questions1.txt paginator_tfidf_lnc_ltc_mwb.txt --mwb ranking.tfidf

python3 main.py searcher results/pubmedSPIMIindexTinytfidf_ltc_ltc/mergedFiles questions/questions1.txt paginator_tfidf_ltc_ltc_mwb.txt --mwb ranking.tfidf

python3 main.py searcher results/pubmedSPIMIindexTinybm25/mergedFiles questions/questions1.txt paginator_bm25_mwb.txt --mwb ranking.bm25
```

### Example of different CLI instructions to run the searcher without Minimum Window Boost, for each schema:

```
python3 main.py searcher results/pubmedSPIMIindexTinytfidf_lnc_ltc/mergedFiles questions/questions1.txt paginator_tfidf_lnc_ltc.txt ranking.tfidf

python3 main.py searcher results/pubmedSPIMIindexTinytfidf_ltc_ltc/mergedFiles questions/questions1.txt paginator_tfidf_ltc_ltc.txt ranking.tfidf

python3 main.py searcher results/pubmedSPIMIindexTinybm25/mergedFiles questions/questions1.txt paginator_bm25.txt ranking.bm25
```

### In order to run searcher for "questions_with_gs" the following argument should be passed:
```
--reader.class QuestionsWithGSReader
```

### Example to run searcher for "questions_with_gs":
```
python3 main.py searcher --reader.class QuestionsWithGSReader results/pubmedSPIMIindexTinytfidf_lnc_ltc/mergedFiles questions_with_gs/question_E8B1_gs.jsonl paginator_tfidf_lnc_ltc.txt ranking.tfidf
```

### Example to run the Exercise 3 script (that gives the results of the metrics):
### It is important to note that the indexes should be created before running the evaluation.py script.
```
python3 evaluationTiny.py

python3 evaluationSmall.py
```
The first command is to run the evaluation with the Tiny collection, and the second command is with the Small collection.

# Statistics

## pubmed_2022_tiny.jsonl.gz
|| 1st try | 2nd try | 3rd try |
|---|---|---|---|
| Ranking                                            | tf-idf (schema lnc.ltc)    | tf-idf (schema ltc.ltc)    | Okapi BM25                 |
| Minimum length filter                              | yes (size 3)               | yes (size 3)               | yes (size 3)               | 
| Stopword filter                                    | yes                        | yes                        | yes                        | 
| Porter stemmer filter                              | yes                        | yes                        | yes                        | 
| Posting threshold                                  | 80000                      | 80000                      | 80000                      | 
| Total indexing time                                | 314.71341347694397 seconds (5 min 14 sec) | 358.14429903030396 seconds (5 min 58 sec) | 315.90995740890503 seconds (5 min 15 sec) | 
| Merging time (last SPIMI step)                     | 16.091875553131104 seconds | 46.89523196220398 seconds  | 33.2069878578186 seconds | 
| Number of temporary index segments written to disk | 128                        | 128                        | 128                        | 
| Total index size on disk                           | 352949870 bytes            | 356173069 bytes            | 342622146 bytes            | 
| Vocabulary size (number of terms)                  | 379588                     | 379588                     | 379588                     | 

## pubmed_2022_small.jsonl.gz

|| 1st try | 2nd try | 3rd try |
|---|---|---|---|
| Ranking                                            | tf-idf (schema lnc.ltc)                  | tf-idf (schema ltc.ltc)                    | Okapi BM25                               |
| Minimum length filter                              | yes (size 3)                             | yes (size 3)                               | yes (size 3)                             |
| Stopword filter                                    | yes                                      | yes                                        | yes                                      |
| Porter stemmer filter                              | yes                                      | yes                                        | yes                                      |
| Posting threshold                                  | 540000                                   | 540000                                     | 540000                                   | 
| Total indexing time                                | 3523.856803257941 seconds (58 min 43 sec) | 3862.254857778549 seconds (1 hr 4 min 22 sec) | 6121.686813354492 seconds (1 hr 42 min 1 sec)|
| Merging time (last SPIMI step)                     | 262.39462750927548 seconds (4 min 22 sec)| 581.4362263679504 seconds (9 min 41 sec)   | 488.6997911930084 seconds (8 min 8 sec)|
| Number of temporary index segments written to disk | 196                                      | 196                                        | 196                                      |
| Total index size on disk                           | 3613077299 bytes                         | 3719759214 bytes                           | 3503781863 bytes                         |
| Vocabulary size (number of terms)                  | 1842238                                  | 1842238                                    | 1842238                                  |



## Exercise 3 Evaluation Metrics for pubmed_2022_tiny.jsonl.gz - BM25
|| 1st try | 2nd try | 3rd try | 4th try | 5th try | 6th try |
|---|---|---|---|---|---|---|
| Evaluation Metrics   | BM25, top-10, with MWB      | BM25, top-10, without MWB      | BM25, top-50, with MWB     | BM25, top-50, without MWB      | BM25, top-100, with MWB      | BM25, top-100, without MWB     |
| Precision            | 0.33375000000000027         | 0.33375000000000027         | 0.09914999999999989        | 0.09914999999999989        | 0.060049999999999965         | 0.060049999999999965        |
| Recall               | 0.7922814930167873          | 0.7922814930167873          | 0.8829282106782105          | 0.8829282106782105          | 0.9165869408369407          | 0.9165869408369407          |
| F-measure            | 0.4011251333000601          | 0.4011251333000601          | 0.15864461085100828         | 0.15864461085100828          | 0.09784776964584084         | 0.09784776964584084         |
| Average Precision    | 0.38138070134684277          | 0.38295411404525553         | 0.16490177727818453         | 0.16490984179431353          | 0.09334503945326236         | 0.09334503945326236         |
| Query Throughput     | 6.091784483464284 queries/s  | 15.223595138050833 queries/s | 5.564204313704878 queries/s | 17.13519489605933 queries/s  | 6.197216295186681 queries/s | 17.750430947872022 queries/s |
| Median query latency | 0.1521683931350708 seconds | 0.054416775703430176 seconds  | 0.15026187896728516 seconds | 0.05061626434326172 seconds | 0.1469271183013916 seconds  | 0.04833555221557617 seconds |

## Exercise 3 Evaluation Metrics for pubmed_2022_tiny.jsonl.gz - TF-IDF (schema lnc.ltc)
|| 1st try | 2nd try | 3rd try | 4th try | 5th try | 6th try |
|---|---|---|---|---|---|---|
| Evaluation Metrics   | lnc-ltc, top-10, with MWB      | lnc-ltc, top-10, without MWB      | lnc-ltc, top-50, with MWB     | lnc-ltc, top-50, without MWB      | lnc-ltc, top-100, with MWB      | lnc-ltc, top-100, without MWB     |
| Precision            | 0.30475000000000024         | 0.30175000000000024         | 0.0983499999999999        | 0.0983499999999999         | 0.05944999999999997         | 0.05944999999999997        |
| Recall               | 0.737192960634137         | 0.7246929606341369          | 0.8701186868686868          | 0.8701186868686868          | 0.8960948773448772          | 0.8960948773448772          |
| F-measure            | 0.36723885241261833          | 0.36247694765071353         | 0.1572813844875884         | 0.1572813844875884          | 0.096711999303798         | 0.096711999303798         |
| Average Precision    | 0.31975618861763827          | 0.31736233941128905         | 0.15005566484310134         | 0.1500067088970866          | 0.10496838595910424         | 0.10496838595910424         |
| Query Throughput     | 3.2665927907379104 queries/s  | 6.231595820236453 queries/s | 3.064954779409621 queries/s | 12.893666379382745 queries/s  | 6.459074472781994 queries/s | 17.016622176739663 queries/s |
| Median query latency | 0.23045051097869873 seconds | 0.11920619010925293 seconds  | 0.25408947467803955 seconds | 0.06315898895263672 seconds | 0.14402008056640625 seconds  | 0.05195975303649902 seconds |

## Exercise 3 Evaluation Metrics for pubmed_2022_tiny.jsonl.gz - TF-IDF (schema ltc.ltc)
|| 1st try | 2nd try | 3rd try | 4th try | 5th try | 6th try |
|---|---|---|---|---|---|---|
| Evaluation Metrics   | ltc-ltc, top-10, with MWB      | ltc-ltc, top-10, without MWB      | ltc-ltc, top-50, with MWB     | ltc-ltc, top-50, without MWB      | ltc-ltc, top-100, with MWB      | ltc-ltc, top-100, without MWB     |
| Precision            | 0.3197500000000002         | 0.3187500000000002         | 0.10134999999999991        | 0.10134999999999991         | 0.060449999999999976         | 0.060449999999999976        |
| Recall               | 0.7501337339131458          | 0.7451337339131457          | 0.9030951744334097         | 0.9030951744334097          | 0.9157002164502164          | 0.9157002164502164          |
| F-measure            | 0.38146246154915325          | 0.37979579488248655         | 0.16245946634756753         | 0.16245946634756753          | 0.09851695638373598        | 0.09851695638373598         |
| Average Precision    | 0.37100068091274324         | 0.37162568091274323        | 0.16417219949556863        | 0.16417219949556863          | 0.09339286815248947         | 0.09339286815248947         |
| Query Throughput     | 6.129490854663104 queries/s  | 16.119458280954014 queries/s | 5.986066121741024 queries/s | 18.124823448105335 queries/s  | 6.246891674298224 queries/s | 17.72594172594291 queries/s |
| Median query latency | 0.15137755870819092 seconds | 0.05309712886810303 seconds  | 0.15100634098052979 seconds | 0.04693031311035156 seconds | 0.14607572555541992 seconds  | 0.048450589179992676 seconds |

## Exercise 3 Evaluation Metrics for pubmed_2022_small.jsonl.gz - BM25
|| 1st try | 2nd try | 3rd try | 4th try | 5th try | 6th try |
|---|---|---|---|---|---|---|
| Evaluation Metrics   | BM25, top-10, with MWB      | BM25, top-10, without MWB      | BM25, top-50, with MWB     | BM25, top-50, without MWB      | BM25, top-100, with MWB      | BM25, top-100, without MWB     |
| Precision            | 0.30200000000000016         | 0.29900000000000015         | 0.1095054054054052        | 0.10960540540540518         | 0.07108539578539569         | 0.07113539578539568        |
| Recall               | 0.6559638284159418          | 0.6481662093683227          | 0.8289679966949787          | 0.829301330028312          | 0.856678746871202          | 0.8583454135378688          |
| F-measure            | 0.34818400925695697          | 0.34430573067279613         | 0.16817707761538322         | 0.16833092376922937          | 0.10934900113059243         | 0.1094460885092332         |
| Average Precision    | 0.3002797127947379          | 0.2992188693227336         | 0.14111707105836924         | 0.14128954407237476          | 0.09945370412656182         | 0.09948689094688795         |
| Query Throughput     | 0.4367620138174529 queries/s  | 1.032608651096577 queries/s | 0.6741367395603531 queries/s | 1.944350974045642 queries/s  | 0.6753880348780141 queries/s | 2.0742196659089718 queries/s |
| Median query latency E8B1 | 2.4911683797836304 seconds | 0.9281826019287109 seconds  | 1.5592361688613892 seconds | 0.4974253177642822 seconds | 1.5276612043380737 seconds  | 0.45355308055877686 seconds |
| Median query latency E8B2 | 1.5574337244033813 seconds | 0.7248376607894897 seconds  | 1.1734527349472046 seconds | 0.3963404893875122 seconds | 1.186663269996643 seconds  | 0.40057289600372314 seconds |

## Exercise 3 Evaluation Metrics for pubmed_2022_small.jsonl.gz - TF-IDF (schema lnc.ltc)
|| 1st try | 2nd try | 3rd try | 4th try | 5th try | 6th try |
|---|---|---|---|---|---|---|
| Evaluation Metrics   | lnc-ltc, top-10, with MWB      | lnc-ltc, top-10, without MWB      | lnc-ltc, top-50, with MWB     | lnc-ltc, top-50, without MWB      | lnc-ltc, top-100, with MWB      | lnc-ltc, top-100, without MWB     |
| Precision            | 0.2650000000000003         | 0.25800000000000034         | 0.10360540540540515        | 0.10270540540540514         | 0.0692353957853957         | 0.0691353957853957        |
| Recall               | 0.5952575239928853         | 0.5751741906595519          | 0.7746723502414038          | 0.7648747311937848          | 0.830539171541729          | 0.8246225048750623          |
| F-measure            | 0.3093474208054805          | 0.30017115540421513         | 0.15805200711263948         | 0.15648386563957437          | 0.10595713012803099         | 0.10575185437224373         |
| Average Precision    | 0.2691484499832736          | 0.2586186172168337         | 0.14898265535164906         | 0.14637062947703217          | 0.10587510340631992         | 0.10582150479624781         |
| Query Throughput     | 0.47723154565845227 queries/s  | 0.6719928773789613 queries/s | 0.4240185321731119 queries/s | 1.4066911686972632 queries/s  | 0.005562858048555774 queries/s | 1.8726991223365934 queries/s |
| Median query latency E8B1 | 1.9901453256607056 seconds | 1.4101612567901611 seconds  | 2.4018301963806152 seconds | 0.6113147735595703 seconds | 1.5662132501602173 seconds  | 0.5264960527420044 seconds |
| Median query latency E8B2 | 1.4455232620239258 seconds | 1.2087153196334839 seconds  | 1.4080286026000977 seconds | 0.6093728542327881 seconds | 1.3037358522415161 seconds  | 0.40615320205688477 seconds |

## Exercise 3 Evaluation Metrics for pubmed_2022_small.jsonl.gz - TF-IDF (schema ltc.ltc)
|| 1st try | 2nd try | 3rd try | 4th try | 5th try | 6th try |
|---|---|---|---|---|---|---|
| Evaluation Metrics   | ltc-ltc, top-10, with MWB      | ltc-ltc, top-10, without MWB      | ltc-ltc, top-50, with MWB     | ltc-ltc, top-50, without MWB      | ltc-ltc, top-100, with MWB      | ltc-ltc, top-100, without MWB     |
| Precision            | 0.2570000000000004         | 0.2510000000000004         | 0.10350540540540519        | 0.1031054054054052         | 0.06883539578539569         | 0.0687353957853957        |
| Recall               | 0.5540963869628226          | 0.5367190975855332          | 0.7701090736132292         | 0.7622757402798959          | 0.8211596261794469          | 0.8183262928461136          |
| F-measure            | 0.29515478777257553          | 0.2873796915346276         | 0.15787888306494938         | 0.15714811383418015        | 0.10522699646604858         | 0.10504200072862319         |
| Average Precision    | 0.2731941738905166        | 0.2643665463758355         | 0.13158209507344693         | 0.1314528494802444         | 0.09597042180953286         | 0.09581515124155608        |
| Query Throughput     | 0.27667205806938516 queries/s  | 1.8024614337953146 queries/s | 0.6632069254833692 queries/s | 1.6503051108981412 queries/s  | 0.666061462251976 queries/s | 2.0221013641136887 queries/s |
| Median query latency E8B1 | 3.007343053817749 seconds | 0.5218029022216797 seconds  | 1.5553112030029297 seconds | 0.6382462978363037 seconds | 1.5522737503051758 seconds  | 0.44116055965423584 seconds |
| Median query latency E8B2 | 2.889098048210144 seconds | 0.4731098413467407 seconds  | 1.2035059928894043 seconds | 0.3853609561920166 seconds | 1.17887544631958 seconds  | 0.3862173557281494 seconds |

# Analysis of the query results
In the root folder of the repository we can find some paginators files, which are the results of the queries performed by the *evaluationSmall.py* and *evaluationTiny.py* scripts.

# Considerations about exercise 2 (Minimum Window Boost)
In order to determine the number of high idf terms per query, we used the following formula:
```
n_high_idf_terms = 8 + math.log( len(query_tokens) , 2 )
```
In order to determine the Maximum Possible Window Size, we used the following formula (if a window is bigger than this, it will be discarded):
```
max_window_size = 2 * n_distinct_query_terms + math.log(n_distinct_query_terms, 2)
```
For the boost, we tried out these two approaches (ending up using the second one):
```
boost = B * n_distinct_query_terms / min_window_size # another approach with worse results
boost = B * ( 1 -  ( (min_window_size - n_distinct_query_terms) / min_window_size ) )
```

# Authors

| NMec | Name | Github |
|--:|---|---|
| 98513 | **Eva Bartolomeu** | [eva-pomposo](https://github.com/eva-pomposo) |
| 98470 | **Artur Romão** | [artur-romao](https://github.com/artur-romao) |
