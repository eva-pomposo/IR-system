#!/bin/bash

# bash command to solve the assignment 1
python3 main.py indexer collections/pubmed_2022_tiny.jsonl.gz pubmedSPIMIindexTiny --tk.minL 2 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 540000
python3 main.py indexer collections/pubmed_2022_small.jsonl.gz pubmedSPIMIindexSmall --tk.minL 2 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 540000
python3 main.py indexer collections/pubmed_2022_medium.jsonl.gz pubmedSPIMIindexMedium --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 540000
python3 main.py indexer collections/pubmed_2022_large.jsonl.gz pubmedSPIMIindexLarge --tk.minL 3 --tk.stopwords stopw.txt --tk.stemmer potterNLTK --indexer.posting_threshold 540000