
# type: ignore
import timeit
from collections import Counter
from typing import Iterable

import nltk
from pprint import pprint
from functional import pseq as sequence
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize

from ytdrama.db import read_channel_vids

# pprint(nltk.help.upenn_tagset())
pprint("*"*100)

videos = read_channel_vids("notsoErudite")
lemmatizer = WordNetLemmatizer()
words = videos[0].transcript.words()


def lemmatize(words: list[str], remove: bool=True):
    global lemmatizer
    
    def not_stopword(word: str) -> bool:
        return word not in stopwords.words("english")
    
    if remove: 
        iterable = filter(not_stopword, words)
    else: 
        iterable = words
    return list(map(lemmatizer.lemmatize, iterable))


def reverse_tuple(input: tuple) -> tuple: 
    return input[::-1]


def count_items(input: tuple[str, list]) -> tuple[str, Counter]: 
    return input[0], Counter(input[1])


def is_adjective(input: tuple[str, str]) -> bool: 
    return input[0] in ("JJ")

counts = (
    sequence(videos)
        .map(lambda video: video.transcript.words())
        .map(lemmatize)
        .map(pos_tag)
        .flatten()
        .map(reverse_tuple)
        .filter(is_adjective)
        .group_by_key()
        .map(count_items)
        .to_list()
)

pprint(counts[0][1].most_common(20))

# pprint({k: v.most_common(10) for k, v in tmp})

# adjectives = { key: value.most_common(10) for key, value in tmp.items() if key.startswith("JJ") }
# pprint(adjectives)
# def method_1(words: list[str]) -> list[str]:
#     tmp = words
#     tmp = map(lambda word: lemmatizer.lemmatize(word), tmp)
#     tmp = filter(lambda word: word.casefold() not in stopwords.words("english"), tmp)
#     tmp = list(tmp)
#     return tmp


# def method_2(words: list[str]) -> list[str]:
#     tmp = list(
#         filter(
#             lambda word: word.casefold() not in stopwords.words("english"),
#             map(lambda word: lemmatizer.lemmatize(word), words),
#         )
#     )
#     return tmp


# pprint(
#     timeit.repeat(
#         setup="from __main__ import method_1",
#         stmt="method_1(['The', 'friends', 'of', 'DeSoto', 'love', 'scarves'])",
#         repeat=1,
#         number=10000,
#     )
# )

# pprint(
#     timeit.repeat(
#         setup="from __main__ import method_2",
#         stmt="method_2(['The', 'friends', 'of', 'DeSoto', 'love', 'scarves'])",
#         repeat=1,
#         number=10000,
#     )
# )

# # pprint(words)

# """
# Tags that start with	Deal with
# JJ =	Adjectives
# NN =	Nouns
# RB =	Adverbs
# PRP =	Pronouns
# VB =	Verbs
# """
# # stemmed = [stemmer.stem(word) for word in words]

# # tags = nltk.pos_tag(words)
# # pprint(tags)
