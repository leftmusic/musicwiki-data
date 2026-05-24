#!/usr/bin/env python3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INDEX_FILE = os.path.join(DATA_DIR, 'index.json')
SONGS_DIR = os.path.join(DATA_DIR, 'songs')
ARTISTS_DIR = os.path.join(DATA_DIR, 'artists')
ALBUMS_DIR = os.path.join(DATA_DIR, 'albums')
