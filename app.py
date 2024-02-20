import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
import pandas as pd
import config


def initialize_spotify():
    scope = "user-read-recently-played"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        config.CLIENT_ID, 
        config.CLIENT_KEY, 
        config.SPOTIPY_REDIRECT_URI, 
        scope=scope))
    
    return sp

def collect_data(sp, date, limit=50):
    timestamp = int(date.timestamp()) * 1000

    return sp.current_user_recently_played(limit=limit, after=timestamp)

def transform(raw_data, date):
    data = []

    for r in raw_data['items']:
        data.append(
            {
                "played_at": r["played_at"],
                "artist": r["track"]["artists"][0]["name"],
                "track": r["track"]["name"]
            }
        )
    input_df = pd.DataFrame(data)
    
    # Remove dates different from what we want
    df = input_df[pd.to_datetime(input_df["played_at"]).dt.date == date.date()]

    # Data validation FTW
    if not df["played_at"].is_unique:
        raise ValueError("A value from played_at is not unique")
    
    if df.isnull().values.any():
        raise ValueError("A value in df is null")
    
    return df

if __name__ == "__main__":
    try:
        date = datetime.today() - timedelta(days=1)

        # Extract
        spotify_instance = initialize_spotify()
        data_raw = collect_data(spotify_instance, date)

        # Transform
        df = transform(data_raw, date)

        print(df)

    except Exception as e:
        print(f"An error occurred: {e}")