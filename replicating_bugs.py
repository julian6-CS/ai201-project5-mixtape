from datetime import datetime, timedelta, timezone
from app import create_app, db
from models import User, Song, Tag, Playlist, ListeningEvent, Rating, Notification, song_tags, playlist_entries, friendships
from services.streak_service import record_listening_event , get_streak , update_listening_streak
from services.feed_service import get_friends_listening_now
from services.search_service import search_songs, get_song
from services.notification_service import get_notifications, add_to_playlist, rate_song
from services.playlist_service import get_user_playlists, create_playlist, get_playlist_songs

#Bug three replication

def testing_bug_five():
    app = create_app()
    with app.app_context():
        listOfUSER = []
        songs = []

        for s in Song.query.all():
            songs.append(s)

        for u in User.query.all():
            listOfUSER.append(u)
        
        user = listOfUSER[0]
        user_id = user[0].id
        playlist = create_playlist(name="new_playlist", created_by_user_id=user_id)
        playlist_id = playlist.id 

        add_to_playlist(playlist_id=playlist_id,song_id=songs[2].id,added_by_user_id=user_id)
        add_to_playlist(playlist_id=playlist_id,song_id=songs[1].id,added_by_user_id=user_id)
        add_to_playlist(playlist_id=playlist_id,song_id=songs[0].id,added_by_user_id=user_id)

        print(get_playlist_songs(playlist_id=playlist_id))


        
        



def testing_bug_four():
    #error
    app = create_app()
    with app.app_context():

        
        listOfUSERIDS = {}
        songs = []
        userAfterLoggingListen = []

        for s in Song.query.all():
            songs.append(s)

        for u in User.query.all():
            listOfUSERIDS[u.id] = u
        
        reccomended_song = songs[2]
        reccomended_by = reccomended_song.shared_by
        userWhoReccomended = listOfUSERIDS.get(reccomended_by)
        friend_ids = [f.id for f in userWhoReccomended.friends]
        print(friend_ids)


        notifications_before_playlist = get_notifications(user_id=userWhoReccomended.id)
        print(notifications_before_playlist)

        # get the first friend of the user who reccomended, add the song to they shared specifically to cause the notification to appear, log the notification
        friend_identification = friend_ids[0]
        friend = listOfUSERIDS.get(friend_identification)
        friends_playlist = create_playlist(name="new_playlist", created_by_user_id=friend_identification)
        friend_playlist_id = friends_playlist.id 

        
        add_to_playlist(playlist_id=friend_playlist_id,song_id=reccomended_song.id,added_by_user_id=friend_identification)
        add_to_playlist(playlist_id=friend_playlist_id,song_id=songs[1].id,added_by_user_id=friend_identification)
        add_to_playlist(playlist_id=friend_playlist_id,song_id=songs[0].id,added_by_user_id=friend_identification)
        print("ADDED SONGS")
        print(get_playlist_songs(playlist_id=friend_playlist_id))
        print("ADDED SONGS")
        print("")

        notifications_after_playlist = get_notifications(user_id=userWhoReccomended.id)
        print("")
        print("")
        print(notifications_after_playlist)
        print("")
        print("")

        
        rate_song( user_id=friend_ids[0],song_id=(reccomended_song.id), score=5)
        notifications_after_review = get_notifications(user_id=userWhoReccomended.id)
        print("")
        print("")
        print(notifications_after_review)
        print("")
        print("")

        if (notifications_after_review == notifications_after_playlist):
            print("No Notification Due to Friend Rating")
        
        print("")
        print("")
        print(f"playlist_id:{friend_playlist_id} , added_by: {friend_identification}, song_id: {reccomended_song.id}")




    






#Bug two replication
def record_listening_event_for_Bug_Replication(user_id: str, song_id: str, time: datetime ) -> ListeningEvent:
    """
    Record that a user listened to a song and update their streak. Just copy pasted the code present in the streak_service.py with the added functionality of passing a time

    Args:
        user_id: The ID of the user who listened.
        song_id: The ID of the song that was listened to.
        time: The intended datetime mainly used to replicate the second bug

    Returns:
        The created ListeningEvent.
    """
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    now = time

    # Create the listening event
    event = ListeningEvent(user_id=user_id, song_id=song_id, listened_at=now)
    db.session.add(event)

    # Update the streak
    update_listening_streak(user, now)

    db.session.commit()
    return event


def testing_bug_two():
    app = create_app()
    with app.app_context():
        listOfUSERIDS = []
        songs = []

        forty_hours_ago = datetime.now(timezone.utc) - timedelta(hours=48)
        events = ListeningEvent.query.all()

        for event in events:
            event.listened_at = forty_hours_ago

        for u in User.query.all():
            u.last_listened_at = forty_hours_ago
        db.session.commit() # Setting the datetime for both objects to a time 23 hours would suffice, but to reproduce the exact workflows done that the user would encounter I vied for this option instead 
        #Otherwise, please run seed.py after replicating each bug just in case


        now = datetime.now(timezone.utc)
        twenty_three_hours_ago = now - timedelta(hours=23)

        for s in Song.query.all():
            songs.append({"id": s.id, "title" : s.title})

        for u in User.query.all():
            listOfUSERIDS.append({"id": u.id, "username" : u.username, "streak" : u.listening_streak})
            record_listening_event_for_Bug_Replication(user_id=u.id,song_id=(songs[0])["id"],time=twenty_three_hours_ago)
        
        list_of_friend_feeds = get_friends_listening_now((listOfUSERIDS[0])["id"])
        print(list_of_friend_feeds)
    


# Bug one replication
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
    #testing_listening_streak()
    testing_bug_four()
    #testing_bug_two()

