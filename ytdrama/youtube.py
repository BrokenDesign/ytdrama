# type: ignore
import logging
from typing import Optional

import googleapiclient.discovery
import googleapiclient.errors
from box import Box
from functional import seq
from dotenv import load_dotenv
from googleapiclient.discovery import Resource
from sqlalchemy.orm import Session
from youtube_transcript_api import YouTubeTranscriptApi

from ytdrama.db import *
from ytdrama.settings import config

logger = logging.getLogger(__name__)

client: Resource = googleapiclient.discovery.build(
    "youtube", "v3", developerKey=config.credentials.api_token
)
# print(str(response).encode("utf-8", "ignore"))

def get_channel_playlists(id: str) -> Optional[tuple[Channel, list[Playlist]]]:
    request = client.channels().list(part="snippet,contentDetails", id=id)  
    response = {}
    try:
        response = request.execute()
        logger.debug(response)
        
        channel = Channel(Box(response))
        playlists = []
        
        for item in response["items"]: 
            playlist = Playlist(Box(item))
            playlists.append(playlist)
            
        logger.debug(channel)
        logger.debug(playlists)
        
        return channel, playlists
    
    except Exception:
        logger.error(f"ERROR: playlist id={id}, response={response}")


def get_playlist_videos(id: str) -> list[Video]:
    request = client.playlistItems().list(
        playlistId=id,
        part='id,snippet,contentDetails',
        maxResults = 5,
    )
    response = {}
    try:
        videos = []
        while request:
            logger.debug(request)
            
            response = request.execute()
            logger.debug(response)
            
            videos = [Video(Box(item)) for item in response['items']]
            request = client.playlistItems().list_next(request, response)
            break
        
        return videos
    
    except Exception as err: 
        logger.error(f"ERROR: video id={id}")
        logger.error(response)
        return []


def get_video_transcript(id: str) -> Optional[Transcript]:
    response = {}
    try:
        response = YouTubeTranscriptApi.get_transcript(id)
        logger.debug("id={id}, response={response}")
        
        transcript = Transcript(Box(response))
        logger.debug(transcript)
        
        return transcript

    except Exception:
        logger.error(f"ERROR: transcript id={id}")
        logger.error(response)


def scrape(ids: list[str]) -> None:
    session = Session(engine)
    
    for id in ids: 
        channel: Optional[Channel] = None
        playlists: list[Playlist] = []
        transcripts: list[Transcript] = []
        
        channel_result = get_channel_playlists(id)
        logger.debug(channel_result)
        
        if channel_result: 
            channel, playlists = channel_result
            
            try: 
                session.add(channel)
                session.add_all(playlists)
                session.commit()
                logger.info(f"Saved channel: {channel}")
                
            except Exception: 
                logger.error(f"Error writing channel for id={id}")
                logger.error(channel)
        
            for playlist in playlists:
                logger.debug(playlist)
                session.add(playlist)
                    
                videos = get_playlist_videos(playlist.id)
                
                if videos: 
                    transcripts = (
                        seq(videos)
                        .map(lambda video: get_video_transcript(video.id))
                        .filter(lambda transcript: transcript is not None)
                        .to_list()
                    ) 
                    try: 
                        session.add_all(transcripts)
                        session.commit()
                        session.flush()
                    
                    except Exception: 
                        logger.error(session)
                        
                    finally: 
                        session.close()
                        

if __name__ == "__main__":
    response = get_channel_playlists("UCyfYnJbsQ20Ee0y_jqDq09A")
    logger.info(response)
    if response is not None: 
        channel, playlist = response
        logger.info(channel)
        logger.info(playlist)
        logger.info("HERE")
#   videos = get_playlist_videos("UUyfYnJbsQ20Ee0y_jqDq09A")
    
  

