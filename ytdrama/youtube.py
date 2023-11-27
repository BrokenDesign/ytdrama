# type: ignore
import logging
from pprint import PrettyPrinter
from typing import Optional

import googleapiclient.discovery
import googleapiclient.errors

from box import Box
from functional import seq
from googleapiclient.discovery import Resource
from youtube_transcript_api import YouTubeTranscriptApi

from ytdrama.db import Playlist, Video
from ytdrama.db import Session
from ytdrama.settings import config

logger = logging.getLogger(__name__)
pp = PrettyPrinter(indent=2)

client: Resource = googleapiclient.discovery.build(
    "youtube", "v3", developerKey=config.credentials.api_token
)


def format(obj):
    global pp
    return f"\n{pp.pformat(obj)}\n"


def get_channel_playlists(id: str) -> Optional[list[Playlist]]:
    logger.info(f"Retrieving channel id={id}")
    request = client.channels().list(part="snippet,contentDetails", id=id)
    try:
        response = request.execute()
        return [Playlist(Box(item)) for item in response["items"]]

    except Exception:
        logger.error(f"ERROR: playlist id={id}")


def get_video_transcript(id: str) -> Optional[list[dict]]:
    logger.info(f"Retrieving transcript id={id}")
    try:
        return YouTubeTranscriptApi.get_transcript(id)
    except Exception:
        logger.error(f"ERROR: transcript id={id}")
        return []


def get_playlist_videos(id: str) -> list[Video]:
    logger.info(f"Retrieving video id={id}")

    def strip_description(data: dict) -> Box:
        assert "snippet" in data, "Missing snippiet"
        assert "description" in data["snippet"], "Missing description"
        data["snippet"]["description"] = (
            data["snippet"]["description"].encode("ascii", errors="ignore").decode()
        )
        return Box(data)

    request = client.playlistItems().list(
        playlistId=id,
        part="id,snippet,contentDetails",
        maxResults=50,
    )
    try:
        videos = []
        while request:
            response = request.execute()
            videos += (
                seq(response["items"])
                .map(strip_description)
                .map(lambda x: (x.snippet.resourceId.videoId, x))  # type: ignore
                .map(lambda x: Video(x[1], get_video_transcript(x[0])))  # type: ignore
                .to_list()  # type: ignore
            )
            request = client.playlistItems().list_next(request, response)

        return videos

    except Exception:
        logger.error(f"ERROR: video id={id}")
        return []


def scrape(ids: list[str]) -> None:
    logger.info(f"Starting scrape...\n\n\n******************* SCRAPE: START\n")
    session = Session()
    for id in ids:
        playlists = get_channel_playlists(id)
        if playlists:
            for playlist in playlists:
                session.add(playlist)
                videos = get_playlist_videos(playlist.id)
                if videos:
                    try:
                        session.add_all(videos)
                        session.commit()
                    except Exception as err:
                        logger.error(f"Error writing playlists for channel id={id}")
                        session.rollback()
                        session.close()
                        raise err
                    finally:
                        session.flush()
                        session.close()
