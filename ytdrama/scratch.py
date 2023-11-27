import logging
from box import Box
from sqlalchemy.orm import Session
from ytdrama.db import * 

logger = logging.getLogger(__name__)

response = {
    "kind": "youtube#channelListResponse",
    "etag": "i-DagdkkIdeKuqtZM1r8zlGOh1I",
    "pageInfo": {"totalResults": 1, "resultsPerPage": 5},
    "items": [
        {
            "kind": "youtube#channel",
            "etag": "k-1o9esDmkAAduabW5vpZHWmj10",
            "id": "UCyfYnJbsQ20Ee0y_jqDq09A",
            "snippet": {
                "title": "notsoErudite",
                "description": "Just a gal, \ncraving some nuance and consistency, \nin a complicated world. ",
                "customUrl": "@notsoerudite",
                "publishedAt": "2021-05-05T08:54:47.170615Z",
                "thumbnails": {
                    "default": {
                        "url": "https://yt3.ggpht.com/ioTe73osneDBdzgnFgs0SnNwN-bqkmvR4E01yjGRT4-PmUiIUf8JJuzEcLQhJ_AQXuSSmRAwpw=s88-c-k-c0x00ffffff-no-rj",
                        "width": 88,
                        "height": 88,
                    },
                    "medium": {
                        "url": "https://yt3.ggpht.com/ioTe73osneDBdzgnFgs0SnNwN-bqkmvR4E01yjGRT4-PmUiIUf8JJuzEcLQhJ_AQXuSSmRAwpw=s240-c-k-c0x00ffffff-no-rj",
                        "width": 240,
                        "height": 240,
                    },
                    "high": {
                        "url": "https://yt3.ggpht.com/ioTe73osneDBdzgnFgs0SnNwN-bqkmvR4E01yjGRT4-PmUiIUf8JJuzEcLQhJ_AQXuSSmRAwpw=s800-c-k-c0x00ffffff-no-rj",
                        "width": 800,
                        "height": 800,
                    },
                },
                "localized": {
                    "title": "notsoErudite",
                    "description": "Just a gal, \ncraving some nuance and consistency, \nin a complicated world. ",
                },
                "country": "CA",
            },
            "contentDetails": {
                "relatedPlaylists": {"likes": "", "uploads": "UUyfYnJbsQ20Ee0y_jqDq09A"}
            },
        }
    ],
}

channel = Channel(Box(response['items'][0]))
# playlist = Playlist(Box(response['items'][0]))
logger.info(channel)
# logger.info(playlist)

with Session(engine) as session: 
    try: 
        session.add(channel)
        # session.add(playlist)
        session.commit()
    except Exception: 
        logger.error('RUH ROH')

logger.info("FINI")

