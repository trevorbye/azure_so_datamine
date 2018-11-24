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

"""
# comment_bodies = APIFetcher.get_comments_from_question_list(question_list)
question_bodies = APIFetcher.get_question_bodies(question_list)
parsed_bodies = UtilityMethods.parse_paragraph_content_from_list_docs(question_bodies)

key_phrases = APIFetcher.key_phrase_extraction(parsed_bodies)


word_list = UtilityMethods.build_wordlist_frm_keyphrases(key_phrases)
df_wordlist = pandas.DataFrame(list(word_list.items()), columns=['Word', 'Freq'])
df_wordlist = df_wordlist.sort_values(by="Freq", ascending=False)

semantic_groups = UtilityMethods.build_cosine_similarity_matrix_from_bodies(key_phrases)
bp = "test"
"""

# pickle.dump(comment_bodies, open("ml_list_comments.pkl", "wb"))
# pickle.dump(question_bodies, open("ml_list_questions.pkl", "wb"))
# ml_question_bodies = pickle.load(open("ml_list_questions.pkl", "rb"))

"""
questions_msdocs_uris = APIFetcher.extract_msdocs_uris_in_text(question_bodies)
msdocs_freq_matrix = APIFetcher.build_msdcos_freq_matrix(questions_msdocs_uris)

attribute_matrix = {}
attribute_matrix["Total Questions"] = int(len(question_bodies))
attribute_matrix["Total msdocs Links"] = int(len(questions_msdocs_uris))
attribute_matrix["Unique msdocs Links"] = int(len(msdocs_freq_matrix))
attribute_matrix["msdocs Links as % of Total Questions"] = (attribute_matrix["Total msdocs Links"]*1.0)/\
                                                      (attribute_matrix["Total Questions"]*1.0)

df_ml_questions = pandas.DataFrame(list(msdocs_freq_matrix.items()), columns=['Article Desc.', 'Link Count'])
df_ml_questions = df_ml_questions.sort_values(by="Link Count", ascending=False)
df_ml_attributes = pandas.DataFrame(list(attribute_matrix.items()), columns=['Attribute', 'Value'])

re_dist = APIFetcher.get_rep_distribution_from_question_list(question_list)
re_dist = [x for x in re_dist if x < 10000]

running_sum = 0
for x in re_dist:
    running_sum = running_sum + x
mean = (running_sum * 1.0) / len(re_dist)
"""

#plot.hist(np.array(re_dist), bins=100, edgecolor="black", color="red")
#plot.title("ml.net Users Rep Distribution:  mean=" + str(round(mean, 2)) + ";  Global SO rep mean=109")
#plot.show()

user_group_list = APIFetcher.build_id_groups_for_batching(question_list, "user_id")
tag_freq_matrix = APIFetcher.build_users_top_tags_freq_matrix(user_group_list, 300)

fig = plot.figure()
ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)

df_ml = pandas.DataFrame(list(tag_freq_matrix.items()), columns=['Tag', 'Count'])
df_ml = df_ml.sort_values(by="Count", ascending=False)


tag_list = df_ml.values.tolist()
df_ml = df_ml.head(20)
df_ml.plot(ax=ax1, kind="bar", title="ml.net")

"""
df_cs = pandas.DataFrame.from_dict(cs_tag_freq, orient="index")
df_cs.columns = ["tag-count"]
df_cs = df_cs.sort_values(by="tag-count", ascending=False)
df_cs = df_cs.head(20)
df_cs.plot(ax=ax2, kind="bar", title="azure-cognitive-services", color="red")
"""

plot.tight_layout()
plot.show()
