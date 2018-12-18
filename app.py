from flask import Flask, jsonify, request, render_template, url_for
import pandas
import APIFetcher
import UtilityMethods
app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template("index.html", title="StackOverflow Datamine Interface")


@app.route("/tags")
def tag_page():
    return render_template("tags.html", title="Tag Research")


@app.route("/devs")
def dev_page():
    return render_template("devs.html", title="Dev Insights")


@app.route("/text-analytics")
def text_page():
    return render_template("text.html", title="Text Analytics")


# /get-tags-from-string-contained?instring=azure&maxbackoffsec=200
@app.route("/get-tags-from-string-contained")
def get_tags():
    search_string_param = request.args.get("instring", default="", type=str)
    max_backoff_param = request.args.get("maxbackoffsec", default=300, type=int)

    tag_list_counts = APIFetcher.get_tag_list_where_includes(search_string_param, max_backoff_param)
    return jsonify(tag_list_counts)


@app.route("/get-dev-profile")
def get_dev_profile():
    response_object = {}
    tag_name = request.args.get("tagname", default="", type=str)

    question_pages = APIFetcher.get_question_page_list_from_tag(tag_name, 300)
    question_list = APIFetcher.get_question_list_from_pages(question_pages)

    user_group_list = APIFetcher.build_id_groups_for_batching(question_list, "user_id")
    tag_freq_matrix = APIFetcher.build_users_top_tags_freq_matrix(user_group_list, 300)

    df = pandas.DataFrame(list(tag_freq_matrix.items()), columns=['Tag', 'Count'])
    df = df.sort_values(by="Count", ascending=False)

    tag_list = df.values.tolist()
    partial_list = tag_list[:20]

    response_object["tagChartData"] = partial_list
    response_object["tagTableData"] = tag_list

    user_rep_list = APIFetcher.get_rep_distribution_from_question_list(question_list)
    response_object["repDistData"] = user_rep_list

    tag_trend_list = UtilityMethods.build_tag_trend_from_datelist(question_list)
    response_object["tagTrendData"] = tag_trend_list

    return jsonify(response_object)


@app.route("/get-text-analytics")
def get_text_analytics():
    response_object = {}
    tag_name = request.args.get("tagname", default="", type=str)

    question_pages = APIFetcher.get_question_page_list_from_tag(tag_name, 300)
    question_list = APIFetcher.get_question_list_from_pages(question_pages)

    question_bodies = APIFetcher.get_question_bodies(question_list)
    parsed_bodies = UtilityMethods.parse_paragraph_content_from_list_docs(question_bodies)

    body_key_phrases = APIFetcher.key_phrase_extraction(parsed_bodies)
    word_list = UtilityMethods.build_wordlist_frm_keyphrases(body_key_phrases)
    df_wordlist = pandas.DataFrame(list(word_list.items()), columns=['Word', 'Freq'])
    df_wordlist = df_wordlist.sort_values(by="Freq", ascending=False)
    table_wordlist = df_wordlist.values.tolist()

    response_object["bodyWordList"] = table_wordlist

    questions_msdocs_uris = APIFetcher.extract_msdocs_uris_in_text(question_bodies)
    msdocs_freq_matrix = APIFetcher.build_msdcos_freq_matrix(questions_msdocs_uris)
    response_object["msDocsUriMatrix"] = msdocs_freq_matrix

    summary_stats = UtilityMethods.build_summary_stats(len(question_bodies), len(questions_msdocs_uris), msdocs_freq_matrix)
    response_object["msDocsSummaryStats"] = summary_stats

    # builds cosine similarity data set
    question_title_bodies = APIFetcher.get_question_title_bodies(question_list)
    key_title_phrases = APIFetcher.key_phrase_extraction(question_title_bodies)

    # parametize this in UI
    pruned_phrases = UtilityMethods.prune_key_phrases(key_title_phrases, 5)
    semantic_groups = UtilityMethods.build_cosine_similarity_matrix_from_bodies(pruned_phrases, 0.2)

    data_object = UtilityMethods.build_semantic_groups_to_output(semantic_groups)
    response_object["cosineSimilarity"] = data_object

    return jsonify(response_object)


@app.route("/refresh-text-analytics")
def refresh_cosine_plot():
    response_object = {}
    tag_name = request.args.get("tagname", default="", type=str)
    prune_val = request.args.get("prune-val", default=5, type=int)
    cosine_val = request.args.get("cosine-val", default=0.2, type=float)

    question_pages = APIFetcher.get_question_page_list_from_tag(tag_name, 300)
    question_list = APIFetcher.get_question_list_from_pages(question_pages)

    # builds cosine similarity data set
    question_title_bodies = APIFetcher.get_question_title_bodies(question_list)
    key_title_phrases = APIFetcher.key_phrase_extraction(question_title_bodies)

    # parametrized in UI
    pruned_phrases = UtilityMethods.prune_key_phrases(key_title_phrases, prune_val)
    semantic_groups = UtilityMethods.build_cosine_similarity_matrix_from_bodies(pruned_phrases, cosine_val)

    data_object = UtilityMethods.build_semantic_groups_to_output(semantic_groups)
    response_object["cosineSimilarity"] = data_object

    return jsonify(response_object)

