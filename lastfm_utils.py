import json

import requests
from pydantic import BaseModel, Field, ValidationError

from config import LASTFM_KEY as KEY


class ArtistBio(BaseModel):
    summary: str = Field(alias="Описание")

    class Config:
        allow_population_by_field_name = True


class ArtistStats(BaseModel):
    # listeners: int = Field(alias="Кол-во слушателей")
    playcount: int = Field(alias="Кол-во прослушиваний")

    class Config:
        allow_population_by_field_name = True


class Artist(BaseModel):
    name: str = Field(alias="Артист")
    url: str = Field(alias="Ссылка")
    stats: ArtistStats
    bio: ArtistBio = Field(alias="Биография")

    class Config:
        allow_population_by_field_name = True


class Album(BaseModel):
    name: str = Field(alias="Альбом")
    playcount: int = Field(alias="Кол-во прослушиваний")
    url: str = Field(alias="Ссылка")

    class Config:
        allow_population_by_field_name = True


def do_request(params: dict) -> dict | None:
    url = "http://ws.audioscrobbler.com/2.0/?"
    r = requests.get(url, params)
    data = json.loads(r.text)
    if "error" in data:
        return None
    return data


def get_artist_info(artist_name: str) -> str | None:
    params = {
        "method": "artist.getinfo",
        "artist": artist_name,
        "api_key": KEY,
        "format": "json",
    }

    artist_data = do_request(params)
    if artist_data is None:
        return None

    try:
        artist = Artist.parse_obj(artist_data["artist"])
        artist_json = json.loads(artist.json(by_alias=True))
    except ValidationError as error:
        print("Exception", error.json())
        return None
    else:
        result = ""
        for key, value in artist_json.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    result += f"{k}: {v}\n"
            else:
                result += f"{key}: {value}\n"
        return result


def get_top_albums(artist_name: str, count: int = 3) -> str | None:
    params = {
        "method": "artist.gettopalbums",
        "artist": artist_name,
        "api_key": KEY,
        "format": "json",
    }

    albums_data = do_request(params)
    if albums_data is None:
        return "Ошибка! Неверное имя артиста."
    albums_json = []
    try:
        for album_data in albums_data["topalbums"]["album"]:
            album = Album.parse_obj(album_data)
            album_json = json.loads(album.json(by_alias=True))
            albums_json.append(album_json)

    except ValidationError as error:
        print("Exception", error.json())
        return None
    else:
        result = ""
        for a in albums_json[:count]:
            for key, value in a.items():
                result += f"{key}: {value}\n"
            result += "\n"
        return result
