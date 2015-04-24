from snapchat import Snapchat
import getpass
from pprint import pprint

# Enter your snapchat credentials (they will be used securely)
USERNAME = #Your Snapchat username
PASSWORD = #Your Snapchat password


TARGET = #Some other Snapchat username
SAVE_TO = "downloaded_snap"
UPLOAD_FROM = #some local file

s = Snapchat(USERNAME, PASSWORD)

# Add a friend by username
s.add_friend(TARGET)


# Get a list (meta-data) of your recent snaps
snap_info = s.get_snaps()
for snap in snap_info:
	print snap
	print "\n\n"


# Download your most recently received snap
# This will fail if you have already opened the snap
snap_id = snap_info[0]['id']
s.download_media(snap_id, SAVE_TO)


# Upload a snap before it can be sent or used in your story
# Use a media type that corresponds to the type of file being uploaded
# i.e. Snapchat.MEDIA_IMAGE or Snapchat.MEDIA_VIDEO
media_id = s.upload(Snapchat.SOME_MEDIA_TYPE, UPLOAD_FROM)

# Send an uploaded snap to another user
s.send(media_id, TARGET)

# Add an uploaded snap to your story
s.add_story(media_id)


s.logout()
