import logging
from typing_extensions import override

from box import Box
from collections import Counter
from datetime import datetime
from functional import seq
from dateutil import parser as date_parser
from sqlalchemy import Column, DATETIME, ForeignKey, PickleType, String, Text
from sqlalchemy import create_engine, create_mock_engine
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column, relationship

from ytdrama.settings import config

logger = logging.getLogger(__name__)
url = f"sqlite:///data/{config.database.name}"
engine = None


class Base(DeclarativeBase):
    def __repr__(self) -> str:
        name = self.__class__.__name__
        items = (
            seq(self.__dict__.items())
            .map(lambda k, v: f"{k}={'...' if isinstance(v, Box) else v}")
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
    playlist_id: Mapped[str] = mapped_column(ForeignKey("playlists.id"))
    playlist: Mapped[Playlist] = relationship("Playlist", foreign_keys=[playlist_id])
    title: Mapped[str] = mapped_column(Text)
    date_published: Mapped[datetime] = mapped_column(DATETIME)
    detail: Mapped[Box] = mapped_column(PickleType)
    _transcript: Mapped[Box] = mapped_column(PickleType)

    def __init__(self, data: Box):
        self.id = data.snippet.id
        self.playlist_id = data.id
        self.title = data.snippet.title
        self.detail = data
        self._transcript = data.transcript

    def _transcript_text(self) -> str:
        return str()

    def _transcript_words(self) -> list[str]:
        return (list())

    def _transcript_data(self) -> Box:
        return self._transcript

    def count_words(self, words: str | list[str]) -> Counter:
        if isinstance(words, str):
            words = [words]
        return Counter(filter(lambda word: word in words, self._transcript_words()))

    @property
    def transcript(self):
        pass

    @transcript.getter
    def transcript(self) -> Box:
        return Box(
            {
                "text": self._transcript_text,
                "words": self._transcript_words,
                "data": self._transcript_data,
            }
        )


def delete():
    pass


def exists(path: str):
    pass


def initialize(mock: bool = False):
    global engine

    def ddl_dump(sql, *multiparams, **params):
        print(sql.compile(dialect=engine.dialect))  # type: ignore

    if mock:
        engine = create_mock_engine(url, ddl_dump)  # type: ignore
    else:
        engine = create_engine(url, echo=True)

    if config.database.overwrite or not exists(config.database.path):
        Base.metadata.create_all(engine, checkfirst=False)


if __name__ == "__main__":
    initialize()
