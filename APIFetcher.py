import requests
import math
import time
import requests
import UtilityMethods
from sklearn.ensemble import IsolationForest
import numpy as np
import pandas
from datetime import datetime

api_key = "uTbSik2jd6UJmkIC3DguOg(("


def get_question_page_list_from_tag(string_tag, max_backoff_wait_time_sec):
    """
    Gets all question pages by tag

    :param string_tag: string representing a SO tag ex. "azure-machine-learning
    :param max_backoff_wait_time_sec: total maximum time in seconds user wishes to wait for backoff, if this time is
           reached, the function will stop polling the API and return the result set it has thus far
    :return: returns a list of pages, use this return as a param to get_question_list_from_pages()
    """

    question_page_list = []
    has_more = True
    accumulated_backoff_time_sec = 0
    page = 1

    base_url = "https://api.stackexchange.com/2.2/questions?order=desc&sort=creation&site=stackoverflow" \
               "&tagged=" + string_tag + "&filter=withbody" + "&pagesize=100&key=" + api_key

    while has_more:
        response = requests.get(base_url + "&page=" + str(page))
        response_dict = response.json()
        question_page_list.append(response_dict["items"])

        # check if response has a backoff param, if so check against max desired wait time and either pause thread
        # or quit polling
        try:
            backoff = response_dict["backoff"]
            accumulated_backoff_time_sec = accumulated_backoff_time_sec + backoff

            if accumulated_backoff_time_sec < max_backoff_wait_time_sec:
                time.sleep(backoff)
            else:
                has_more = False
        except:
            pass

        # the "has_more" parameter in the response object indicates there are more pages
        query_has_more_pages = response_dict["has_more"]
        if not query_has_more_pages:
            has_more = False

        # cut sample size at 25 pages (2500 entities) to avoid excessive API calls
        if page >= 25:
            break

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


def get_question_bodies(question_list):
    list_question_bodies = []

    for question in question_list:
        list_question_bodies.append(question["body"])

    return list_question_bodies


def get_question_title_bodies(question_list):
    list_title_bodies = []
    list_question_urls = []

    for question in question_list:
        list_title_bodies.append(question["title"])
        list_question_urls.append(question["link"])

    return_dict = {"bodies": list_title_bodies, "links": list_question_urls}

    return return_dict


def build_id_groups_for_batching(question_list, id_type):
    """
    Builds unique id_list from questions, puts id's into groups of 80 to avoid excessive API requests

    :param question_list: return val from get_question_list_from_pages
    :param id_type: string name for id type, extracts different id from question object
    :return: list of group lists
    """

    # build unique id list
    id_list = []
    for question in question_list:
        if id_type == "user_id":
            try:
                user_id = question["owner"]["user_id"]
                if user_id not in id_list:
                    id_list.append(user_id)
            except:
                pass
        else:
            id_list.append(question["question_id"])

    # build unique id's into groups to limit the amount of API requests
    id_list_size = len(id_list)
    num_groups = 0

    if id_list_size <= 100:
        num_groups = 1
    else:
        num_groups = math.ceil(id_list_size / 100)

    list_of_group_lists = []
    index_start = 0
    index_end = 99
    for i in range(num_groups):
        group_list = [x for x in id_list if index_start <= id_list.index(x) <= index_end]
        list_of_group_lists.append(group_list)

        index_start = index_start + 100
        index_end = index_end + 100

    return list_of_group_lists


def build_users_top_tags_freq_matrix(user_group_list, max_backoff_wait_time_sec):
    """
    Takes user groups and hits the API for each user's top profile tags. This allows you to see, independent
    of the tag you searched for to fetch the question_list, what other tags do they work with.
    Builds total count of questions/answers for each unique tag, from each user.

    :param user_group_list: return from build_user_groups_for_batching()
    :return: dict (map of unique tag, and total question/answer count for that tag
    """

    accumulated_backoff_time_sec = 0
    tag_freq_map = {}
    # for each user group, fetch their top used tags and add to map
    for user_group in user_group_list:

        # build chained user string for this user group
        chained_user_string = ""
        for user_id in user_group:
            chained_user_string = chained_user_string + str(user_id) + ";"

        chained_user_string = chained_user_string[:-1]

        base_url = "https://api.stackexchange.com/2.2/users/" + chained_user_string + "/top-tags?site=stackoverflow" \
                   + "&key=" + api_key
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

        # check if response has a backoff param, if so check against max desired wait time and either pause thread
        # or quit polling
        try:
            backoff = response_dict["backoff"]
            accumulated_backoff_time_sec = accumulated_backoff_time_sec + backoff

            if accumulated_backoff_time_sec < max_backoff_wait_time_sec:
                time.sleep(backoff)
            else:
                break
        except:
            pass

    return tag_freq_map


def get_rep_distribution_from_question_list(question_list):

    rep_list = []
    for question in question_list:

        # if a user account no longer exists, "owner" object will not exist and throw exception
        try:
            rep = question["owner"]["reputation"]
            rep_list.append(rep)
        except:
            pass

    np_array = np.array(rep_list)
    reshaped = np_array.reshape((-1, 1))
    clf = IsolationForest(contamination=0.03)
    outliers = clf.fit_predict(reshaped)
    outliers_as_list = np.array(outliers).tolist()

    cleaned_list = []
    ind = 0
    for rep in rep_list:
        outlier_val = outliers_as_list[ind]
        if outlier_val == 1:
            cleaned_list.append(rep)
        ind = ind + 1

    return cleaned_list


def get_tag_list_where_includes(include_string, max_backoff_wait_time_sec):

    has_more = True
    accumulated_backoff_time_sec = 0
    page = 1
    base_url = "https://api.stackexchange.com/2.2/tags?order=desc&sort=popular&site=stackoverflow" \
               "&pagesize=100" + "&inname=" + include_string + "&key=" + api_key

    tag_object_list = []
    tag_array_list = []
    while has_more:
        response = requests.get(base_url + "&page=" + str(page))
        response_dict = response.json()

        tag_list = response_dict['items']
        tag_rank = 0
        for tag_obj in tag_list:
            # only build the top tag with this attribute
            if page == 1 and tag_rank == 0:
                new_obj = {"name": tag_obj["name"], "y": tag_obj["count"], "sliced": True, "selected": True}

            else:
                new_obj = {"name": tag_obj["name"], "y": tag_obj["count"]}

            array_obj_for_table = [tag_obj["name"], tag_obj["count"]]

            tag_array_list.append(array_obj_for_table)
            tag_object_list.append(new_obj)
            tag_rank = tag_rank + 1
        try:
            backoff = response_dict["backoff"]
            accumulated_backoff_time_sec = accumulated_backoff_time_sec + backoff

            if accumulated_backoff_time_sec < max_backoff_wait_time_sec:
                time.sleep(backoff)
            else:
                has_more = False
        except:
            pass

        # the "has_more" parameter in the response object indicates there are more pages
        query_has_more_pages = response_dict["has_more"]
        if not query_has_more_pages:
            has_more = False

        page = page + 1

    return_obj = {"chartData": tag_object_list, "tableData": tag_array_list}

    return return_obj


def get_comments_from_question_list(question_list):
    question_id_group_list = build_id_groups_for_batching(question_list, "question_id")

    all_comment_entities_list = []
    for question_id_group in question_id_group_list:

        # build chained user string for this user group
        chained_id_string = ""
        for question_id in question_id_group:
            chained_id_string = chained_id_string + str(question_id) + ";"

        chained_id_string = chained_id_string[:-1]

        base_url = "https://api.stackexchange.com/2.2/questions/" + chained_id_string + "/comments?order=desc" \
                   "&sort=creation&site=stackoverflow&filter=withbody&key=" + api_key
        response = requests.get(base_url)
        response_dict = response.json()

        all_comment_entities_list.append(response_dict["items"])

    comment_body_list = []
    for group in all_comment_entities_list:
        for comment_entity in group:
            body = comment_entity["body"]
            comment_body_list.append(body)

    return comment_body_list


def extract_msdocs_uris_in_text(list_of_documents):
    """
    Finds occurrences where someone linked to msdocs url path in a body of text. In case there are multiple msdocs uris
    anchors in the text body, find them in order and remove the root uri as you find each one, and the loop will
    continue grabbing them until there are none left

    :param list_of_documents: list of strings
    :return: list of dicts
    """

    root_test_string = "<a href=\"https://docs.microsoft.com"
    msdocs_url_objects = []

    # build list of msdocs urls
    for doc in list_of_documents:
        scan_for_uris = True

        while scan_for_uris:
            if root_test_string in doc:

                # extract path, article desc, and rebuild full url
                path = doc.split(root_test_string)[1].split("\"")[0]

                if "#" in path:
                    path = path.split("#")[0]

                if path.endswith("/"):
                    path = path[:-1]

                article_desc = path.rpartition("/")[-1]
                full_url = "https://docs.microsoft.com" + path

                url_object = [full_url, article_desc]
                msdocs_url_objects.append(url_object)

                # delete only first occurrence of root URI
                doc = doc.replace(root_test_string, "", 1)
            else:
                break

    return msdocs_url_objects


def build_msdcos_freq_matrix(list_of_msdcos_objects):
    df = pandas.DataFrame(list_of_msdcos_objects, columns=['URL', 'Article'])
    df.index.name = "id"
    df = df.groupby(["URL", "Article"]).Article.agg("count").to_frame("Count").reset_index()
    df = df.sort_values(by="Count", ascending=False)
    df_as_list = df.values.tolist()

    return df_as_list


def key_phrase_extraction(list_of_docs, list_LINKS):
    base_url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/keyPhrases"
    subscription_key = "a3d9dbb3f8904b2cbc465bfa5b2284f4"

    list_size = len(list_of_docs)
    num_groups = 0

    if list_size <= 1000:
        num_groups = 1
    else:
        num_groups = math.ceil(list_size / 1000)

    list_of_group_lists = []
    list_of_group_lists_LINKS = []
    index_start = 0
    index_end = 999
    for i in range(num_groups):
        group_list = [x for x in list_of_docs if index_start <= list_of_docs.index(x) <= index_end]
        LINK_group_list = [x for x in list_LINKS if index_start <= list_LINKS.index(x) <= index_end]

        list_of_group_lists.append(group_list)
        list_of_group_lists_LINKS.append(LINK_group_list)

        index_start = index_start + 1000
        index_end = index_end + 1000

    list_aggregated_phrases = []
    corresponding_LINK_list = []

    for group, link_group in zip(list_of_group_lists, list_of_group_lists_LINKS):

        list_doc_dicts = []
        total_chars = 0
        id = 1
        for doc, link in zip(group, link_group):
            char_len = len(doc)
            total_chars += char_len
            if total_chars > 524000:
                break

            tmp_dict = {"id": id, "language": "en", "text": doc}
            list_doc_dicts.append(tmp_dict)
            corresponding_LINK_list.append(link)
            id = id + 1

        documents = {"documents": list_doc_dicts}
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        response = requests.post(base_url, headers=headers, json=documents)
        key_phrases = response.json()
        docs = key_phrases["documents"]

        for doc in docs:
            combined_string = ""
            phrases = doc["keyPhrases"]
            for phrase in phrases:
                combined_string = combined_string + " " + phrase

            duplicates_removed = UtilityMethods.remove_duplicates(combined_string)
            list_aggregated_phrases.append(duplicates_removed)

    return_dict = {"phrases": list_aggregated_phrases, "links": corresponding_LINK_list}

    return return_dict


def build_views_ranking(question_list):
    return_list = []

    for question in question_list:
        unix_timestamp = question["creation_date"]
        parsed_date = datetime.utcfromtimestamp(unix_timestamp).strftime("%m-%d-%Y")

        record = [question["title"], question["view_count"], parsed_date, question["link"]]
        return_list.append(record)

    return return_list
