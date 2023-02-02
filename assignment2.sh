#!/bin/bash

# bash command to solve the assignment 2
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinyLncLtc --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.tfidf.cache_in_disk
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinyLtcLtc --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.tfidf.smart ltc.ltc --indexer.tfidf.cache_in_disk
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinyBm25  --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.bm25.cache_in_disk 

python3 main.py searcher results/pubmedSPIMIindexTinyLncLtc/mergedFiles questions/questions1.txt paginator_tfidf_lnc_ltc.txt ranking.tfidf
python3 main.py searcher results/pubmedSPIMIindexTinyLtcLtc/mergedFiles questions/questions1.txt paginator_tfidf_ltc_ltc.txt ranking.tfidf
python3 main.py searcher results/pubmedSPIMIindexTinyBm25/mergedFiles questions/questions1.txt paginator_bm25.txt ranking.bm25