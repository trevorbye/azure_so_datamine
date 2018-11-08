import APIFetcher
import matplotlib.pyplot as plot
import pandas
import csv
import pickle

ml_question_pages = APIFetcher.get_question_page_list_from_tag("azure-machine-learning", 300)
question_list = APIFetcher.get_question_list_from_pages(ml_question_pages)
comment_list = APIFetcher.get_comments_from_question_list(question_list)
#pickle.dump(comment_list, open("list_comments.pkl", "wb"))
question_bodies = APIFetcher.get_question_bodies(question_list)

msdcos_urls = APIFetcher.extract_msdocs_uris_in_text(comment_list)
xx_urls = APIFetcher.extract_msdocs_uris_in_text(question_bodies)




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