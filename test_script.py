import APIFetcher
import UtilityMethods
import matplotlib.pyplot as plot
import pandas
import numpy as np
import csv
import pickle

#tag_list = APIFetcher.get_tag_list_where_includes("azure-cognitive-services", 200)

question_pages = APIFetcher.get_question_page_list_from_tag("azure-cognitive-services", 300)
question_list = APIFetcher.get_question_list_from_pages(question_pages)

question_title_bodies = APIFetcher.get_question_title_bodies(question_list)
key_title_phrases = APIFetcher.key_phrase_extraction(question_title_bodies)

# removes most commonly used words for better semantic comparison
pruned_phrases = UtilityMethods.prune_key_phrases(key_title_phrases, 0.011)

semantic_groups = UtilityMethods.build_cosine_similarity_matrix_from_bodies(pruned_phrases, 0.2)
data_list = UtilityMethods.build_semantic_groups_to_output(semantic_groups)
bp = "test"
