import requests
from pprint import pprint
import pickle
import matplotlib.pyplot as plot
import numpy as np

#base_url = "https://api.stackexchange.com/2.2/tags?order=desc&sort=popular&site=stackoverflow&inname=azure&pagesize=100"
#response = requests.get(base_url)
#response_dict = response.json()

#tag_list = response_dict['items']

# pickle to avoid calling this API multiple times for the same tag list
#pickle.dump(tag_list, open("C:\\Users\\trbye\\python_pickles\\tags.pkl", "wb"))
tag_list = pickle.load(open("C:\\Users\\trbye\\python_pickles\\tags.pkl", "rb"))
tags = []
counts = []

for tag_obj in tag_list:
    tags.append(tag_obj["name"])
    counts.append(tag_obj["count"])

tags.pop(0)
counts.pop(0)

y_pos = np.arange(len(tags))

plot.bar(y_pos, counts, align='center')
plot.xticks(y_pos, tags, rotation=45)
plot.tight_layout()
#plot.show()

pprint(tag_list)

