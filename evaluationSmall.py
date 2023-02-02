import json
import os
import time

for ranking in ["bm25", "tfidf_lnc_ltc", "tfidf_ltc_ltc"]:
    for top_k in [10, 50, 100]:
        for mwb in ["", "--mwb"]:
            query_throughput = time.time()
            os.system("python3 main.py searcher --reader.class QuestionsWithGSReader results/pubmedSPIMIindexSmall" + ranking + "/mergedFiles questions_with_gs/question_E8B1_gs.jsonl paginator1_" + ranking + "_top" + str(top_k) + mwb + ".txt --top_k " + str(top_k) + " " + mwb + " ranking." + ranking.split("_")[0])
            os.system("python3 main.py searcher --reader.class QuestionsWithGSReader results/pubmedSPIMIindexSmall" + ranking + "/mergedFiles questions_with_gs/question_E8B2_gs.jsonl paginator2_" + ranking + "_top" + str(top_k) + mwb + ".txt --top_k " + str(top_k) + " " + mwb + " ranking." + ranking.split("_")[0])
            query_throughput = time.time() - query_throughput

            paginator1 = open("paginator1_" + ranking + "_top" + str(top_k) + mwb + ".txt", "r")
            paginator2 = open("paginator2_" + ranking + "_top" + str(top_k) + mwb + ".txt", "r")

            precision, recall, f_measure, ap, median_query_latency, num_queries = 0, 0, 0, 0, 0, 0

            # Open the JSONL file in read mode
            with open('questions_with_gs/question_E8B1_gs.jsonl', 'r') as f:
                for line in f:
                    # Load the line as a JSON object
                    query = json.loads(line)
                    num_queries += 1
                    
                    # Extract the list of relevant documents
                    relevant_documents = set(query['documents_pmid'])

                    # Extract the list of retrieved documents
                    documents_retrieved = set()
                    paginator1.readline()
                    line = paginator1.readline()
                    while line != "\n":
                        documents_retrieved.add(line.split()[1])
                        line = paginator1.readline()

                    # Compute precision, recall and f-measure
                    precision_tmp = len(documents_retrieved.intersection(relevant_documents)) / len(documents_retrieved)
                    recall_tmp = len(documents_retrieved.intersection(relevant_documents)) / len(relevant_documents)
                    precision += precision_tmp
                    recall += recall_tmp
                    f_measure += (2 * precision_tmp * recall_tmp) / (precision_tmp + recall_tmp) if (precision_tmp + recall_tmp) != 0 else 0
                    
                    # Compute average precision
                    ap_tmp = 0
                    found_relevant_docs = 0
                    for i,doc in enumerate(documents_retrieved):
                        if doc in relevant_documents:
                            found_relevant_docs += 1
                            ap_tmp += found_relevant_docs / (i + 1)
                    ap_tmp /= len(relevant_documents)
                    ap += ap_tmp

            with open('questions_with_gs/question_E8B2_gs.jsonl', 'r') as f:
                for line in f:
                    # Load the line as a JSON object
                    query = json.loads(line)
                    num_queries += 1
                    
                    # Extract the list of relevant documents
                    relevant_documents = set(query['documents_pmid'])

                    # Extract the list of retrieved documents
                    documents_retrieved = set()
                    paginator2.readline()
                    line = paginator2.readline()
                    while line != "\n":
                        documents_retrieved.add(line.split()[1])
                        line = paginator2.readline()

                    # Compute precision, recall and f-measure
                    precision_tmp = len(documents_retrieved.intersection(relevant_documents)) / len(documents_retrieved)
                    recall_tmp = len(documents_retrieved.intersection(relevant_documents)) / len(relevant_documents)
                    precision += precision_tmp
                    recall += recall_tmp
                    f_measure += (2 * precision_tmp * recall_tmp) / (precision_tmp + recall_tmp) if (precision_tmp + recall_tmp) != 0 else 0

                    # Compute average precision
                    ap_tmp = 0
                    found_relevant_docs = 0
                    for i,doc in enumerate(documents_retrieved):
                        if doc in relevant_documents:
                            found_relevant_docs += 1
                            ap_tmp += found_relevant_docs / (i + 1)
                    ap_tmp /= len(relevant_documents)
                    ap += ap_tmp

            precision /= num_queries
            recall /= num_queries
            f_measure /= num_queries
            ap /= num_queries
            query_throughput = num_queries / query_throughput

            print()
            if mwb == "":
                print("Evaluation metrics for collection Small, " + ranking + " , top-" + str(top_k) + " without mwb:")
            else:
                print("Evaluation metrics for collection Small, " + ranking + " , top-" + str(top_k) + " with mwb:")
            print("Precision: " + str(precision))
            print("Recall: " + str(recall))
            print("F-measure: " + str(f_measure))
            print("Average Precision: " + str(ap))
            print("Query Throughput: " + str(query_throughput))
            print("E8B1, ", paginator1.readline())
            print("E8B2, ", paginator2.readline())
            print()
            paginator1.close()
            paginator2.close()