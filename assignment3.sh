#!/bin/bash

# bash command to solve the assignment 3
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinytfidf_lnc_ltc --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.tfidf.cache_in_disk
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinytfidf_ltc_ltc --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.tfidf.smart ltc.ltc --indexer.tfidf.cache_in_disk
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTinybm25  --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 80000 --indexer.bm25.cache_in_disk 

python3 main.py searcher results/pubmedSPIMIindexTinytfidf_lnc_ltc/mergedFiles questions/questions1.txt paginator_tfidf_lnc_ltc.txt ranking.tfidf
python3 main.py searcher results/pubmedSPIMIindexTinytfidf_ltc_ltc/mergedFiles questions/questions1.txt paginator_tfidf_ltc_ltc.txt ranking.tfidf
python3 main.py searcher results/pubmedSPIMIindexTinybm25/mergedFiles questions/questions1.txt paginator_bm25.txt ranking.bm25

python3 main.py searcher results/pubmedSPIMIindexTinytfidf_lnc_ltc/mergedFiles questions/questions1.txt paginator_tfidf_lnc_ltc_mwb.txt --mwb ranking.tfidf
python3 main.py searcher results/pubmedSPIMIindexTinytfidf_ltc_ltc/mergedFiles questions/questions1.txt paginator_tfidf_ltc_ltc_mwb.txt --mwb ranking.tfidf
python3 main.py searcher results/pubmedSPIMIindexTinybm25/mergedFiles questions/questions1.txt paginator_bm25_mwb.txt --mwb ranking.bm25

python3 evaluationTiny.py
python3 evaluationSmall.py