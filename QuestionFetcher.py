import requests
import pickle
import matplotlib.pyplot as plot
import pandas
import math


def get_question_page_list_from_tag(string_tag):
    """
    Gets all question pages by tag

    :param string_tag: string representing a SO tag ex. "azure-machine-learning
    :return: returns a list of pages, use this return as a param to get_question_list_from_pages()
    """

    question_page_list = []
    has_more = True
    page = 1

    base_url = "https://api.stackexchange.com/2.2/questions?order=desc&sort=activity&site=stackoverflow" \
               "&tagged=" + string_tag + "&pagesize=100"

    while has_more:
        response = requests.get(base_url + "&page=" + str(page))
        response_dict = response.json()
        question_page_list.append(response_dict["items"])

        # the "has_more" parameter in the response object indicates there are more pages
        query_has_more_pages = response_dict["has_more"]
        if not query_has_more_pages:
            has_more = False

        page = page + 1

    return question_page_list


def get_question_list_from_pages(question_page_list):
    """
    Takes list of question pages and builds one main list of all question objects

    :param question_page_list: return val from get_question_page_list_from_tag()
    :return: list of question objects
    """

    question_list = []
    for page in question_page_list:
        for question in page:
            question_list.append(question)

    return question_list


def build_user_groups_for_batching(question_list):
    """
    Builds unique user_id list from questions, puts users into groups of 80 to avoid excessive API requests,

    :param question_list: return val from get_question_list_from_pages
    :return: list of group lists
    """

    user_id_list = []

    # build unique user id list
    for question in question_list:

        try:
            user_id = question["owner"]["user_id"]
            if user_id not in user_id_list:
                user_id_list.append(user_id)
        except:
            pass

    # build unique users into groups to limit the amount of API requests
    user_size = len(user_id_list)
    num_groups = 0

    if user_size <= 80:
        num_groups = 1
    else:
        num_groups = math.ceil(user_size / 80)

    list_of_group_lists = []
    index_start = 0
    index_end = 79
    for i in range(num_groups):
        group_list = [x for x in user_id_list if index_start <= user_id_list.index(x) <= index_end]
        list_of_group_lists.append(group_list)

        index_start = index_start + 80
        index_end = index_end + 80

    return list_of_group_lists


def build_users_top_tags_freq_matrix(user_group_list):
    """
    Takes user groups and hits the API for each user's top profile tags. This allows you to see, independent
    of the tag you searched for to fetch the question_list, what other tags do they work with.
    Builds total count of questions/answers for each unique tag, from each user.

    :param user_group_list: return from build_user_groups_for_batching()
    :return: dict (map of unique tag, and total question/answer count for that tag
    """

    tag_freq_map = {}
    # for each user group, fetch their top used tags and add to map
    for user_group in user_group_list:

        # build chained user string for this user group
        chained_user_string = ""
        for user_id in user_group:
            chained_user_string = chained_user_string + str(user_id) + ";"

        chained_user_string = chained_user_string[:-1]

        base_url = "https://api.stackexchange.com/2.2/users/" + chained_user_string + "/top-tags?site=stackoverflow"
        response = requests.get(base_url)
        response_dict = response.json()
        tag_entity_list = response_dict["items"]

        for tag_entity in tag_entity_list:
            tag_name = tag_entity["tag_name"]
            total_questions_and_answers = tag_entity["answer_count"] + tag_entity["question_count"]

            if tag_name not in tag_freq_map:
                tag_freq_map[tag_name] = total_questions_and_answers
            else:
                current_freq = tag_freq_map[tag_name]
                incremented_freq = current_freq + total_questions_and_answers
                tag_freq_map[tag_name] = incremented_freq

    return tag_freq_map






# list_to_pickle = get_question_list_from_tag("azure-machine-learning")
# pprint(list_to_pickle)
# pickle.dump(list_to_pickle, open("C:\\Users\\trbye\\python_pickles\\azure-ml-questions.pkl", "wb"))


ml_question_pages = pickle.load(open("C:\\Users\\trbye\\python_pickles\\azure-ml-questions.pkl", "rb"))
question_list = get_question_list_from_pages(ml_question_pages)
user_group_list = build_user_groups_for_batching(question_list)
tag_freq_matrix = build_users_top_tags_freq_matrix(user_group_list)


# cs_question_pages = get_question_page_list_from_tag("azure-cognitive-services")
# pickle.dump(cs_question_pages, open("C:\\Users\\trbye\\python_pickles\\azure-cs-questions.pkl", "wb"))

cs_question_pages = pickle.load(open("C:\\Users\\trbye\\python_pickles\\azure-cs-questions.pkl", "rb"))
cs_question_list = get_question_list_from_pages(cs_question_pages)
cs_user_group_list = build_user_groups_for_batching(cs_question_list)
cs_tag_freq = build_users_top_tags_freq_matrix(cs_user_group_list)

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


# in the future, will need to account for multiple users posting more than one question. However,
# it shouldn't affect the total histogram significantly for testing purposes
rep_list = []
for question in question_list:
    try:
        rep = question["owner"]["reputation"]

        if rep <= 10000:
            rep_list.append(rep)
    except:
        rep_list.append(0)

plot.hist(rep_list, bins=50)
plot.show()
