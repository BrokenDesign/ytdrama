from typing import Iterator
import pandas as pd
import tomllib as toml
from box import Box
from functional import seq as sequence

from ytdrama.db import Video
from ytdrama.db import read_channel_vids
from collections import Counter
from pprint import PrettyPrinter

import pandas as pd
from tabulate import tabulate
pp = PrettyPrinter(indent=2)


videos = read_channel_vids("notsoErudite")

words_per_video = list(map(lambda video: len(list(video.transcript.words())), videos))


df = pd.DataFrame([{
    "videos (total)": len(videos),
    "words (min)": min(words_per_video),
    "words (max)": max(words_per_video),
    "words (mean)": sum(words_per_video) / len(videos),
    "words (total)": sum(words_per_video)
}])

df = df.melt(var_name="STAT", value_name="VALUE")

print(
    tabulate(df, tablefmt="psql", floatfmt=".0f", showindex=False, headers="keys") # type: ignore
)
       

