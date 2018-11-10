import APIFetcher
import matplotlib.pyplot as plot
import pandas
import csv
import pickle

ml_question_pages = APIFetcher.get_question_page_list_from_tag("azure-cognitive-services", 300)
question_list = APIFetcher.get_question_list_from_pages(ml_question_pages)

# comment_bodies = APIFetcher.get_comments_from_question_list(question_list)
question_bodies = APIFetcher.get_question_bodies(question_list)

# pickle.dump(comment_bodies, open("ml_list_comments.pkl", "wb"))
# pickle.dump(question_bodies, open("ml_list_questions.pkl", "wb"))
# ml_question_bodies = pickle.load(open("ml_list_questions.pkl", "rb"))
ml_questions_msdocs_uris = APIFetcher.extract_msdocs_uris_in_text(question_bodies)
ml_questions_freq_matrix = APIFetcher.build_msdcos_freq_matrix(ml_questions_msdocs_uris)

attribute_matrix = {}
attribute_matrix["Total Questions"] = int(len(question_bodies))
attribute_matrix["Total msdocs Links"] = int(len(ml_questions_msdocs_uris))
attribute_matrix["Unique msdocs Links"] = int(len(ml_questions_freq_matrix))
attribute_matrix["msdocs Links as % of Total Questions"] = (attribute_matrix["Total msdocs Links"]*1.0)/\
                                                      (attribute_matrix["Total Questions"]*1.0)

df_ml_questions = pandas.DataFrame(list(ml_questions_freq_matrix.items()), columns=['Article Desc.', 'Link Count'])
df_ml_questions = df_ml_questions.sort_values(by="Link Count", ascending=False)
df_ml_attributes = pandas.DataFrame(list(attribute_matrix.items()), columns=['Attribute', 'Value'])


bp = ""
"""
user_group_list = APIFetcher.build_user_groups_for_batching(question_list)
tag_freq_matrix = APIFetcher.build_users_top_tags_freq_matrix(user_group_list, 300)

cs_question_pages = APIFetcher.get_question_page_list_from_tag("azure-cognitive-services", 300)
cs_question_list = APIFetcher.get_question_list_from_pages(cs_question_pages)
cs_user_group_list = APIFetcher.build_user_groups_for_batching(cs_question_list)
cs_tag_freq = APIFetcher.build_users_top_tags_freq_matrix(cs_user_group_list, 300)

fig = plot.figure()
ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)

df_ml = pandas.DataFrame.from_dict(tag_freq_matrix, orient="index")
df_ml.columns = ["tag-count"]
df_ml = df_ml.sort_values(by="tag-count", ascending=False)
df_ml = df_ml.head(20)
df_ml.plot(ax=ax1, kind="bar", title="azure-machine-learning")

df_cs = pandas.DataFrame.from_dict(cs_tag_freq, orient="index")
df_cs.columns = ["tag-count"]
df_cs = df_cs.sort_values(by="tag-count", ascending=False)
df_cs = df_cs.head(20)
df_cs.plot(ax=ax2, kind="bar", title="azure-cognitive-services", color="red")

plot.tight_layout()
plot.show()
"""