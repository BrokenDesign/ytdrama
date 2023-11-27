import logging
import os
from typing import Iterable

from box import Box
from collections import Counter
from datetime import datetime
from functional import seq
from dateutil import parser as date_parser
from sqlalchemy import Engine, DATETIME, ForeignKey, PickleType, String, Text
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, sessionmaker
from sqlalchemy.orm import mapped_column, relationship

from ytdrama.settings import config


logger: logging.Logger = logging.getLogger(__name__)

engine: Engine
Session: sessionmaker

class Base(DeclarativeBase):
    def __repr__(self) -> str:
        def format(value):
            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")
            elif isinstance(value, Box | dict | list):
                return "..."
            else:
                return str(value)

        name = self.__class__.__name__
        items = (
            seq(self.__dict__.items())
            .filter(lambda x: x[0] != "_sa_instance_state")
            .map(lambda x: f"{x[0]}={format(x[1])}")  # type: ignore
            .make_string(", ")  # type: ignore
        )
        return f"{name}({items})"


class Playlist(Base):
    __tablename__ = "playlists"
    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(24))
    name: Mapped[str] = mapped_column(String(32))
    date_created: Mapped[datetime] = mapped_column(DATETIME)
    details: Mapped[Box] = mapped_column(PickleType)

    def __init__(self, data: Box) -> None:
        self.id = data.contentDetails.relatedPlaylists.uploads
        self.channel_id = data.id
        self.name = data.snippet.title
        self.date_created = date_parser.parse(data.snippet.publishedAt)
        self.details = data


class Video(Base):
    __tablename__ = "videos"
    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(24))
    channel_name: Mapped[str] = mapped_column(String(32))
    playlist_id: Mapped[str] = mapped_column(ForeignKey("playlists.id"))
    # playlist: Mapped[Playlist] = relationship(Playlist, foreign_keys=[playlist_id])
    title: Mapped[str] = mapped_column(Text)
    date_published: Mapped[datetime] = mapped_column(DATETIME)
    detail: Mapped[Box] = mapped_column(PickleType)
    _transcript: Mapped[list] = mapped_column(PickleType)

    def __init__(self, data: Box, transcript: list[dict]):
        self.id = data.snippet.resourceId.videoId
        self.channel_id = data.snippet.channelId
        self.channel_name = data.snippet.channelTitle
        self.playlist_id = data.snippet.playlistId
        self.title = data.snippet.title
        self.date_published = date_parser.parse(data.snippet.publishedAt)
        self.detail = data
        self._transcript = transcript

    def _transcript_text(self) -> str:
        return " ".join([item["text"] for item in self._transcript])
    
    def _transcript_words(self) -> Iterable:
        for item in self._transcript: 
            for word in item["text"].split():
                yield word

    def _transcript_data(self) -> list[dict]:
        return self._transcript
    
    @property
    def has_transcript(self) -> bool: 
        return len(self._transcript) > 0
    
    @property
    def transcript(self) -> Box:
        return Box( 
            data = self._transcript_data,
            text = self._transcript_text,
            words = self._transcript_words
        )


url: str = f"sqlite:///data/{config.database.name}"
engine = create_engine(url)
Session = sessionmaker(bind=engine, future=True )

def initialize(mock: bool = False):
    if os.path.isfile(f"data/{config.database.name}"):
        return None

    logger.info("Initializing database...")
    engine = create_engine(url, echo=True)
    Base.metadata.create_all(engine, checkfirst=False)
    

def read_channel_vids(channel_name: str, transcripts_only=True) -> list[Video]:
    with Session(future=True) as session:
        statement = select(Video).filter_by(channel_name=channel_name)
        videos = session.execute(statement).scalars().all() # type: ignore
        
    if transcripts_only:
        videos = list(filter(lambda x: x.has_transcript, videos))   
        
    return videos



