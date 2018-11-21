from bs4 import BeautifulSoup as bs
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer


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


def build_cosine_similarity_matrix_from_bodies(list_doc_key_terms):
    similarity_coeff = 0.2
    list_semantic_groups = []
    vectorizer = TfidfVectorizer(min_df=1)

    for term_string in list_doc_key_terms:
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




