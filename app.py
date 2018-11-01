from flask import Flask
from flask import jsonify
from flask import request
import APIFetcher
app = Flask(__name__)


# /get-tags-from-string-contained?instring=azure&maxbackoffsec=200
@app.route("/get-tags-from-string-contained")
def get_tags():
    search_string_param = request.args.get("instring", default="", type=str)
    max_backoff_param = request.args.get("maxbackoffsec", default=300, type=int)

    tag_list_counts = APIFetcher.get_tag_list_where_includes(search_string_param, max_backoff_param)
    return jsonify(tag_list_counts)


