from flask import Flask, jsonify, request, render_template, url_for
import pandas
import APIFetcher
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

    return jsonify(response_object)

