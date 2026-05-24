#!/usr/bin/env python3
import json
import os
import uuid
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

def generate_short_uuid():
    return uuid.uuid4().hex[:8]

def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"songs": {}, "artists": {}, "albums": {}}

def save_index(index):
    from datetime import datetime, timezone
    index["generatedAt"] = datetime.now(timezone.utc).isoformat()
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def create_wiki_files_for_song(song_id):
    os.makedirs(os.path.join(SONGS_DIR, 'lyrics'), exist_ok=True)
    
    md_file = os.path.join(SONGS_DIR, f'{song_id}.md')
    if not os.path.exists(md_file):
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 歌曲百科\n\n待补充...\n")
    
    plist_file = os.path.join(SONGS_DIR, f'{song_id}.plist')
    if not os.path.exists(plist_file):
        with open(plist_file, 'w', encoding='utf-8') as f:
            json.dump({"contributors": [], "lastEdited": "", "revision": 0}, f, ensure_ascii=False, indent=2)
    
    lyrics_json = os.path.join(SONGS_DIR, 'lyrics', f'{song_id}_zh-CN.json')
    if not os.path.exists(lyrics_json):
        with open(lyrics_json, 'w', encoding='utf-8') as f:
            json.dump({"songId": song_id, "language": "zh-CN", "type": "word-by-word", "lines": []}, f, ensure_ascii=False, indent=2)
    
    lyrics_plist = os.path.join(SONGS_DIR, 'lyrics', f'{song_id}_zh-CN.plist')
    if not os.path.exists(lyrics_plist):
        with open(lyrics_plist, 'w', encoding='utf-8') as f:
            json.dump({"contributors": [], "lastEdited": "", "revision": 0}, f, ensure_ascii=False, indent=2)

def add_song(args):
    index = load_index()
    song_id = f"song_{generate_short_uuid()}"
    song = {
        "id": song_id,
        "title": args.title,
        "artistIds": args.artist_ids.split(',') if args.artist_ids else [],
        "albumId": args.album_id if args.album_id else None,
        "releaseDate": args.release_date,
        "genres": args.genres.split(',') if args.genres else [],
        "lyrics": args.lyrics,
        "musicUrl": "",
        "neteaseId": None
    }
    
    os.makedirs(SONGS_DIR, exist_ok=True)
    with open(os.path.join(SONGS_DIR, f'{song_id}.json'), 'w', encoding='utf-8') as f:
        json.dump(song, f, ensure_ascii=False, indent=2)
    
    create_wiki_files_for_song(song_id)
    
    index["songs"][song_id] = {"title": args.title}
    
    for aid in song["artistIds"]:
        if aid and aid in index["artists"]:
            artist_path = os.path.join(ARTISTS_DIR, f'{aid}.json')
            if os.path.exists(artist_path):
                with open(artist_path, 'r', encoding='utf-8') as f:
                    artist = json.load(f)
                if song_id not in artist["songIds"]:
                    artist["songIds"].append(song_id)
                    with open(artist_path, 'w', encoding='utf-8') as f:
                        json.dump(artist, f, ensure_ascii=False, indent=2)
    
    if args.album_id and args.album_id in index["albums"]:
        album_path = os.path.join(ALBUMS_DIR, f'{args.album_id}.json')
        if os.path.exists(album_path):
            with open(album_path, 'r', encoding='utf-8') as f:
                album = json.load(f)
            if song_id not in album["songIds"]:
                album["songIds"].append(song_id)
                with open(album_path, 'w', encoding='utf-8') as f:
                    json.dump(album, f, ensure_ascii=False, indent=2)
    
    save_index(index)
    print(f"Created song: {song_id} - {args.title}")

def add_artist(args):
    index = load_index()
    artist_id = f"artist_{generate_short_uuid()}"
    artist = {
        "id": artist_id,
        "name": args.name,
        "birthDate": args.birth_date or "",
        "genres": args.genres.split(',') if args.genres else [],
        "songIds": args.song_ids.split(',') if args.song_ids else [],
        "albumIds": args.album_ids.split(',') if args.album_ids else [],
        "bio": args.bio or ""
    }
    
    os.makedirs(ARTISTS_DIR, exist_ok=True)
    with open(os.path.join(ARTISTS_DIR, f'{artist_id}.json'), 'w', encoding='utf-8') as f:
        json.dump(artist, f, ensure_ascii=False, indent=2)
    
    index["artists"][artist_id] = {"name": args.name}
    save_index(index)
    print(f"Created artist: {artist_id} - {args.name}")

def add_album(args):
    index = load_index()
    album_id = f"album_{generate_short_uuid()}"
    album = {
        "id": album_id,
        "title": args.title,
        "artistIds": args.artist_ids.split(',') if args.artist_ids else [],
        "songIds": args.song_ids.split(',') if args.song_ids else [],
        "releaseDate": args.release_date or "",
        "type": args.type or "录音室专辑"
    }
    
    os.makedirs(ALBUMS_DIR, exist_ok=True)
    with open(os.path.join(ALBUMS_DIR, f'{album_id}.json'), 'w', encoding='utf-8') as f:
        json.dump(album, f, ensure_ascii=False, indent=2)
    
    index["albums"][album_id] = {"title": args.title}
    
    for aid in album["artistIds"]:
        if aid and aid in index["artists"]:
            artist_path = os.path.join(ARTISTS_DIR, f'{aid}.json')
            if os.path.exists(artist_path):
                with open(artist_path, 'r', encoding='utf-8') as f:
                    artist = json.load(f)
                if album_id not in artist["albumIds"]:
                    artist["albumIds"].append(album_id)
                    with open(artist_path, 'w', encoding='utf-8') as f:
                        json.dump(artist, f, ensure_ascii=False, indent=2)
    
    save_index(index)
    print(f"Created album: {album_id} - {args.title}")

def list_items(args):
    index = load_index()
    if args.type == 'all':
        print(f"Songs: {len(index.get('songs', {}))}")
        print(f"Artists: {len(index.get('artists', {}))}")
        print(f"Albums: {len(index.get('albums', {}))}")
    else:
        items = index.get(args.type + 's', {})
        for id, info in items.items():
            print(f"{id}: {info.get('title', info.get('name'))}")

def add_batch_songs(args):
    import csv
    index = load_index()
    artist_map = {info["name"]: aid for aid, info in index["artists"].items()}
    album_map = {info["title"]: alid for alid, info in index["albums"].items()}
    song_map = {info["title"]: sid for sid, info in index["songs"].items()}
    
    count = 0
    with open(args.file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) < 3:
                continue
            title, artist_name, release_date = row[0].strip(), row[1].strip(), row[2].strip()
            album_name = row[3].strip() if len(row) > 3 else ""
            genres = row[4].strip() if len(row) > 4 else ""
            
            if title in song_map:
                continue
            
            artist_id = artist_map.get(artist_name, "")
            if not artist_id:
                artist_id = f"artist_{generate_short_uuid()}"
                artist = {
                    "id": artist_id, "name": artist_name, "birthDate": "",
                    "genres": genres.split(',') if genres else [],
                    "songIds": [], "albumIds": [], "bio": ""
                }
                os.makedirs(ARTISTS_DIR, exist_ok=True)
                with open(os.path.join(ARTISTS_DIR, f'{artist_id}.json'), 'w', encoding='utf-8') as f:
                    json.dump(artist, f, ensure_ascii=False, indent=2)
                index["artists"][artist_id] = {"name": artist_name}
                artist_map[artist_name] = artist_id
            
            album_id = ""
            if album_name and album_name not in album_map:
                album_id = f"album_{generate_short_uuid()}"
                album = {
                    "id": album_id, "title": album_name, "artistIds": [artist_id],
                    "songIds": [], "releaseDate": release_date[:4] if release_date else "", "type": "录音室专辑"
                }
                os.makedirs(ALBUMS_DIR, exist_ok=True)
                with open(os.path.join(ALBUMS_DIR, f'{album_id}.json'), 'w', encoding='utf-8') as f:
                    json.dump(album, f, ensure_ascii=False, indent=2)
                index["albums"][album_id] = {"title": album_name}
                album_map[album_name] = album_id
            elif album_name:
                album_id = album_map[album_name]
            
            song_id = f"song_{generate_short_uuid()}"
            song = {
                "id": song_id, "title": title, "artistIds": [artist_id],
                "albumId": album_id, "releaseDate": release_date[:4] if release_date else "",
                "genres": genres.split(',') if genres else [], "lyrics": "",
                "musicUrl": "", "neteaseId": None
            }
            os.makedirs(SONGS_DIR, exist_ok=True)
            with open(os.path.join(SONGS_DIR, f'{song_id}.json'), 'w', encoding='utf-8') as f:
                json.dump(song, f, ensure_ascii=False, indent=2)
            
            create_wiki_files_for_song(song_id)
            index["songs"][song_id] = {"title": title}
            song_map[title] = song_id
            
            artist_path = os.path.join(ARTISTS_DIR, f'{artist_id}.json')
            with open(artist_path, 'r', encoding='utf-8') as f:
                artist = json.load(f)
            if song_id not in artist["songIds"]:
                artist["songIds"].append(song_id)
                with open(artist_path, 'w', encoding='utf-8') as f:
                    json.dump(artist, f, ensure_ascii=False, indent=2)
            
            if album_id:
                album_path = os.path.join(ALBUMS_DIR, f'{album_id}.json')
                with open(album_path, 'r', encoding='utf-8') as f:
                    album = json.load(f)
                if song_id not in album["songIds"]:
                    album["songIds"].append(song_id)
                    with open(album_path, 'w', encoding='utf-8') as f:
                        json.dump(album, f, ensure_ascii=False, indent=2)
            
            count += 1
    
    save_index(index)
    print(f"Added {count} songs from {args.file}")

def main():
    parser = argparse.ArgumentParser(description='MusicWiki Data Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    song_parser = subparsers.add_parser('add-song', help='Add a new song')
    song_parser.add_argument('--title', required=True)
    song_parser.add_argument('--artist-ids', default='')
    song_parser.add_argument('--album-id', default=None)
    song_parser.add_argument('--release-date', required=True)
    song_parser.add_argument('--genres', default='')
    song_parser.add_argument('--lyrics', default='')
    song_parser.set_defaults(func=add_song)
    
    artist_parser = subparsers.add_parser('add-artist', help='Add a new artist')
    artist_parser.add_argument('--name', required=True)
    artist_parser.add_argument('--birth-date', default='')
    artist_parser.add_argument('--genres', default='')
    artist_parser.add_argument('--song-ids', default='')
    artist_parser.add_argument('--album-ids', default='')
    artist_parser.add_argument('--bio', default='')
    artist_parser.set_defaults(func=add_artist)
    
    album_parser = subparsers.add_parser('add-album', help='Add a new album')
    album_parser.add_argument('--title', required=True)
    album_parser.add_argument('--artist-ids', default='')
    album_parser.add_argument('--song-ids', default='')
    album_parser.add_argument('--release-date', default='')
    album_parser.add_argument('--type', default='录音室专辑')
    album_parser.set_defaults(func=add_album)
    
    batch_parser = subparsers.add_parser('add-batch', help='Add songs from CSV file')
    batch_parser.add_argument('--file', required=True, help='CSV file path')
    batch_parser.set_defaults(func=add_batch_songs)
    
    list_parser = subparsers.add_parser('list', help='List items')
    list_parser.add_argument('--type', default='all', choices=['all', 'song', 'artist', 'album'])
    list_parser.set_defaults(func=list_items)
    
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
