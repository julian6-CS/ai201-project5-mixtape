from datetime import datetime, timedelta, timezone
from app import create_app, db
from models import User, Song, Tag, Playlist, ListeningEvent, Rating, Notification, song_tags, playlist_entries, friendships
from services.streak_service import record_listening_event , get_streak , update_listening_streak



def testing_listening_streak():

    app = create_app()
    with app.app_context():

        
        listOfUSERIDS = []
        songs = []
        userAfterLoggingListen = []

        for s in Song.query.all():
            songs.append({"id": s.id, "title" : s.title})

        for u in User.query.all():
            listOfUSERIDS.append({"id": u.id, "username" : u.username, "streak" : u.listening_streak})
            print(get_streak(u.id))
            print("// record a listening event//")
            event = record_listening_event(u.id, (songs[0])["id"])
            print(get_streak(u.id))
            print("// Update a listening event//")
            now = datetime.now(timezone.utc)
            days_since_saturday = (now.weekday() + 1) % 7
            last_saturday = now - timedelta(days=days_since_saturday)
            event = update_listening_streak(u, now=last_saturday)
            print(get_streak(u.id))
            print("NEW ENTRY")
            print("*" * 60)
    
#one for every bug we're reporting 
        
        
        
        



if __name__ == "__main__":
    testing_listening_streak()

