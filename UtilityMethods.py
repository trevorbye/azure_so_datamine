from bs4 import BeautifulSoup as bs
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import time
from datetime import datetime
import pandas


def parse_paragraph_content_from_list_docs(list_docs):
    list_paragraphs = []

    for doc in list_docs:
        parser = bs(doc, features="html.parser")

        for element in parser.findAll(["pre", "code", "a", "em"]):
            element.clear()

        text = parser.get_text().replace("\n", " ")
        list_paragraphs.append(text)

    return list_paragraphs


def remove_duplicates(input):
    input = input.split(" ")

    for i in range(0, len(input)):
        input[i] = "".join(input[i])

    unique = Counter(input)

    s = " ".join(unique.keys())
    return s


def build_cosine_similarity_matrix_from_bodies(list_doc_key_terms, similarity_coeff=0.2):
    list_semantic_groups = []
    vectorizer = TfidfVectorizer(min_df=1)
    removed_empty_strings = [x for x in list_doc_key_terms if not x == ""]

    for term_string in removed_empty_strings:
        if len(list_semantic_groups) == 0:
            semantic_group = {"semantic-group": [term_string]}
            list_semantic_groups.append(semantic_group)
        else:
            # test current term_group against all existing semantic groups. If it isn't similar to any of them,
            # put in it's own new semantic group
            put_in_own_group = True

            for semantic_group in list_semantic_groups:
                add_to_group = True
                list_key_phrase_strings = semantic_group["semantic-group"]

                for key_phrase_string in list_key_phrase_strings:

                    tfidf = vectorizer.fit_transform([key_phrase_string, term_string])
                    cosine_sim = (tfidf * tfidf.T).A[0, 1]

                    if cosine_sim < similarity_coeff:
                        add_to_group = False
                        break

                if add_to_group:
                    list_key_phrase_strings.append(term_string)
                    put_in_own_group = False
                    break

            # if it never got added to a semantic group, put in its own
            if put_in_own_group:
                semantic_group = {"semantic-group": [term_string]}
                list_semantic_groups.append(semantic_group)

    return list_semantic_groups


def build_wordlist_frm_keyphrases(list_key_phrases):
    word_count_map = {}

    for phrase in list_key_phrases:
        for word in phrase.split():
            text = word.lower()

            if text in word_count_map:
                curr_count = word_count_map[text]
                curr_count = curr_count + 1
                word_count_map[text] = curr_count
            else:
                word_count_map[text] = 1

    return word_count_map


def build_tag_trend_from_datelist(question_list):

    list_times = [x["creation_date"] for x in question_list]
    list_times.sort()
    # test = [datetime.utcfromtimestamp(y).strftime('%Y-%m-%d %H:%M:%S') for y in list_times]

    tmp_start_time = list_times[0]
    current_time = time.time()
    secs_in_week = 604800
    tmp_end_time = tmp_start_time + secs_in_week

    list_weeks_question_counts = []
    while tmp_end_time < current_time:

        question_count = 0
        for time_val in list_times:
            if tmp_start_time <= time_val < tmp_end_time:
                question_count = question_count + 1

            if time_val >= tmp_end_time:
                break

        time_marker_object = [tmp_start_time, question_count]
        list_weeks_question_counts.append(time_marker_object)

        tmp_start_time = tmp_end_time
        tmp_end_time = tmp_end_time + secs_in_week

    # multiply unix time by 1000 to get milliseconds for javascript compatibility
    for week in list_weeks_question_counts:
        val = week[0]
        val = val * 1000
        week[0] = val

    return list_weeks_question_counts


def build_summary_stats(question_body_count, msdocs_link_count, matrix):
    summary_object = {}
    summary_object["totalQuestions"] = question_body_count
    summary_object["totalLinks"] = msdocs_link_count
    summary_object["uniqueLinks"] = len(matrix)
    summary_object["linksPercent"] = (summary_object["totalLinks"]*1.0) / \
                                                             (summary_object["totalQuestions"]*1.0)

    return summary_object


def prune_key_phrases(key_phrases, prune_size=5):
    word_list = build_wordlist_frm_keyphrases(key_phrases)
    df_wordlist = pandas.DataFrame(list(word_list.items()), columns=['Word', 'Freq'])
    df_wordlist = df_wordlist.sort_values(by="Freq", ascending=False)
    df_as_list = df_wordlist.values.tolist()

    # get first n words to remove
    words_to_remove = df_as_list[:prune_size]
    remove_list = [x[0] for x in words_to_remove]

    pruned_key_phrases = []
    for phrase in key_phrases:
        lowered = phrase.lower()

        for word in remove_list:
            if word in lowered:
                lowered = lowered.replace(word, "")

        lowered = ' '.join(lowered.split())
        pruned_key_phrases.append(lowered)

    return pruned_key_phrases


def build_semantic_groups_to_output(semantic_groups):
    data_list = []
    max_val = 0

    for group in semantic_groups:
        unique_words = []
        phrase_list = group["semantic-group"]

        for phrase in phrase_list:
            phrase_word_list = phrase.split()

            for phrase_word in phrase_word_list:
                if phrase_word not in unique_words:
                    unique_words.append(phrase_word)

        name = ', '.join(unique_words)
        value = len(phrase_list)
        if value > max_val:
            max_val = value

        data_object = {"name": name, "value": value}
        data_list.append(data_object)

    plot_object_list = []
    for val in range(max_val):
        series_object = {"name": str(val) + " question(s)"}
        data = [x for x in data_list if x["value"] == val]
        series_object["data"] = data
        plot_object_list.append(series_object)

    reversed_and_cleaned = []
    for obj in reversed(plot_object_list):
        if len(obj["data"]) > 0:
            reversed_and_cleaned.append(obj)

    return reversed_and_cleaned
