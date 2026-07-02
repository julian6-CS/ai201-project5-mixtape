# Codebase Map


| # | File_Description | File Name |
|---|-------|-----------------|
| 1 | initiates the flask application, registers the routes to the application by registering the blueprints, and connects to the local mixtape.db database  | `app.py` |
| 2 | Defines get_friends_listening which gets the list of friends associated with the user_id, to then query all the listening events in the database for every friend within a certain cutoff time. The most recent song for each friend is then returned. It also defines get_activity_feed where it fulfills a similar request but without a specified cutoff time and only returns the N most recent listening events.   | `feed_service.py` |
| 3 | Defines search_song which queries into the database for song entries with titles containing a specified string and get_song which quieries for a song using a specific id. The results are returned as dictionary objects to be used by the caller or songs.py. | `search_service.py` |
| 4 | Defines the create_notifications function which simply stores and returns a notification object with the parameters from the request. Add_to_playlist stores a song to the users playlist and if the song was shared by anyone it would alert the person who shared it. Rate_song stores the rating of the user within the a table in the local database using the user id and song id to add a rating object into the database. get_notifications retrieves a list of notification objects tied to a specific user id from the database to then return as dictionary objects. Mark_as_read simply queiries a notification object tied to a specific id to then mark the read variable as true | `notification_service.py` |
| 5 | Defines the record_listening_event function where it creates a listening event object using the user id and song id to then add to the user object stored in the database. Update_listening_streak uses a user object and logs the number of consecutive days they have used this progarm based on the last_listened_at variable in the object to see whether a full day has passed or not. Get_streak simply retrives the user object from the database using the user_id to find it, and returns the variable of listening streak from the object. | `streak_service.py` |
| 6 | The route or api endpoint which handles requests related to the feed functionality. It validates incoming requests, and call the feed_service.py to retrieve listening acivity from the friends associated to their profile. It returns a JSON object containing a list of listenening events and the size of the list for later usage.| `feed.py` |
| 7 | This defines the get_playlist_songs functionality which creates and adds a playlist object to the database. The get_playlist_songs is then able to get the ordered list of songs by retrieving the playlist using the playlist id to then get the list of songs associated with the playlist within the database. get_playlist retrieves the playlist object by querying the playlist entry with the playlist id associated with the object. Get_user_playlists queries for all the playlist objects within the database that hold the user_id within the created_by entry within the database.| `playlists_service.py` |
| 8 | This defines the endpoint which handles all the playlist functionality and validates all the information provided to the api request. It utilizes the playlists_services program to retrieve or update the neccessary information. It then returns a json object containing the requested information. | `playlists.py` |
| 8 | This is the endpoint handling all the functionality associated with songs like searching, logging a listening event, or rating it. After validating the information provided, it utilizes notifications_services.py and streak_services.py to either retrive or record the specified information. Returning a structured JSON response containing the requested information for later use. | `songs.py` |
| 9 | This defines the api endpoint for all functionality associated with the user class like logging streaks, getting notifications, or marking notifications as read. After validating the user input, it uses the programs provided by the streak_services.py and notification_service.py files to log or retrieve the neccessary information. It then returns a JSON object containing the requested information  | `users.py` |

Describing how a users' listening now feed is populated: When a user views or accesses the feed to see what their friends are listening to, a request leading to the "/<user_id>/listening-now" route is placed for a JSON response containing a list of ListeningEvents. The endpoint then calls the get_friends_listening_now() function provided by the feed_services.py file with the user_id as a parameter. The get_friends_listening_now() function retrieves the User object from the database, if there is is entry associated to the user_id it will raise a ValueError. Otherwise, it will calculate a time cutoff where entries made before this cutoff will not be requested. Using the user object retrieved earlier, the friends list will be retrieved from the friends variable so it can then request all the listening events stored in the database associated with one of the friends in the list and created after the cutoff time. This list of listening entries is then cleaned to only contain the one most recent listening event per friend. A list of dictionary objects containing the friend id, the song, and the time they listened to the song is returned. The endpoint then returns a JSON object with this list labeled as "feed: and the size of this list as "count". I presume that this list is then propogated to the users view where they can then see what the most recent song their friend has listened to in the last 24 hours.

# Bug Fix Analysis

Bug Analysis: Bug 1, My listening streak keeps resetting located in `streak_service.py`

Reproduction Steps: To replicate this bug, we must call the update_listening_streak function with a user id and a date entry on a Sunday to trigger the bugs condition. The testing_listening_streak() within the replicating_bugs.py does this exactly and this behavior can be seen right after seeding the database.

Navigation strategy: To fully understand the workflow and the path of the data, to best understand how the functions in streak_service.py is expected to behave I investigated the models.py, user.py, and song.py. I first wanted to understand the object that holds the information utilizes in the functions, seeing that many of the functions in streak_service.py relied on a local variable stored in the User class. I then followed the user.py and song.py files, seeing how the record_listening_event or get_streak is called and it's intended use cases. This helped me understand the work flow intended for the functions so I can better understand what they were meant to achieve and if there were any unexpressed rules or expectations implied by the workflow. I first examined the get_streak functions to see if the error was from incorrect data or incorrect reporting, but the function was so simple and well written that the only other possible cause is some incorrect data entry. Prompted by this discovery, I explored the record_streak functions, I learned that the majority of the function was retrieving the user object, adding a listening event, and calling the update_listening_streak function. I knew it couldn't be caused by adding a listening event because any incorrect data or logic in this addition wouldn't affect the get_streak function. Most of the workflows that would alert the user to their streak resetting utilizes get_streak or the user object. I couldn't indentify any errors with the programming so I followed the workflow into the update_listening_streak function where I evaluated portions of logic which led to the listening_streak getting set back to one. This led me to the lines 73 and 76 where I tested the logic from statements with different examples and I learned that on Sundays where today.weekday() is equal 6 is evaluated as true, the listening streak is then set to one. To be entirely sure of my decision, I emulated many possible examples and I saw that specifically when a date landing on a Sunday is provided to the update_listening_streak function, the listening_streak variable is set to one in user object associated with the user id used in the function call .

Root cause explanation:

When the update_listening_streak is called it requires a user id and a date defined by the datetime library, this object can then be called so any user can receive a simple explanation of the date like .weekday() which provides the specific day a date lands by returning an int value representing the day. On line 73 within the streak-service.py file there is a piece of broken logic where in order for a users' listening streak to be increased the last accessed day from the user has to be one calendar day away from today. For the streak to increment, it must also be called on any day other than a Sunday or where .weekday() does not equal to 6, otherwise the entry ends up on the else clause where the entries' listening streak is set to 1. I evaluated every function and workflow involved with the listening_streak variable to see if this is expected behavior, arriving to the realization that this is unexpected behavior and the listening streak should continue to increment regardless of the day under the right conditions. This change in the user object is then stored in the database and the error is propogated to everything access the listening_streak variable inside of the user object, displaying incorrect data when get_streak() is called.


Fix description: Within the update_listening_streak function, I had to remove the "and today.weekday() != 6" clause from the "elif days_since_last == 1 and today.weekday() != 6" on line 73, clause causes the listening streak to be set to 1 since entries on sunday fail the clause forcing it into the else statement used to set the streak back to one. This is counter-intuitive because the expected functionality from a streak should only reset if a day is missed and is not dependent on any day at all.

Side-effect check:

Prior to finding this error, I evaluated the many functions or workflows involved with the variable of listening_streak inside the User object and functions within the streak_service.py. The only workflows that could be possibly impacted through this change is the feed functionality since the altered function also logs in a listening event which the feed functionality depends on to create a users feed. I first evaluated whether the changes could affect the function later on by evaluating the workflows involved with the feed functionality functions and how the addition of a new listening event object could potentially break logic, arriving to the conclusion that these workflows are safe in spite of the bug being fixed. To make sure, I ran two tests, where added a listening object before and after the changes put in place so I can then run get_activity_feed to see if there are any discrepencies. I tracked the listening event object and compared the output from this workflows to make sure nothing was impacted.

--------------------------------------------------------------------------------------------

Bug Analysis: 

Reproduction Steps: 

Navigation strategy: 

Root cause explanation:

Fix description:

Side-effect check:

--------------------------------------------------------------------------------------------

Bug Analysis: 

Reproduction Steps: 

Navigation strategy: 

Root cause explanation:

Fix description:

Side-effect check:


--------------------------------------------------------------------------------------------

Bug Analysis: 

Reproduction Steps: 

Navigation strategy: 

Root cause explanation:

Fix description:

Side-effect check:


# AI Usage