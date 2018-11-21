from flask import Flask, jsonify, request, render_template, url_for
import APIFetcher
app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template("index.html", title="StackOverflow Datamine Interface")


@app.route("/tags")
def tag_page():
    return render_template("tags.html", title="Tag Research")


# /get-tags-from-string-contained?instring=azure&maxbackoffsec=200
@app.route("/get-tags-from-string-contained")
def get_tags():
    search_string_param = request.args.get("instring", default="", type=str)
    max_backoff_param = request.args.get("maxbackoffsec", default=300, type=int)

    tag_list_counts = APIFetcher.get_tag_list_where_includes(search_string_param, max_backoff_param)
    return jsonify(tag_list_counts)


