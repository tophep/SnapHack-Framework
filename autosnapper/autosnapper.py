from snapchat import Snapchat
import getpass
from pprint import pprint
import os
import errno
import datetime
import time
from pymongo import MongoClient
from random import randint


USERNAME = #Your Snapchat username
PASSWORD = #Your Snapchat password
DOWNLOAD_PATH = os.getcwd() + "/downloads/"			#directory where snap media is stored

DB = MongoClient()["autosnapper"]					
PENDING_SNAPS_TABLE = DB["pending_snaps"]

MAX_FAILURES = 5									#number of crashes tolerated
SKIP_REVIEW = False									#skipping review automatically posts to story
DELETE_MEDIA = True									#delete image and video files after review
DELETE_DATA = True									#delete meta data in DB after review

MIN_SLEEP = 60 										#shortest/longest wait time (in seconds) between 
MAX_SLEEP = 600										#subsequent updates



#######################
######## Tasks ########
#######################

def get_analytics(user):
	data = user.get_updates()
	for story in data["stories_response"]["my_stories"]:			#for each active story
		print story["story_extras"]["view_count"]					#get its number of views
		
	print str(  len(data["updates_response"]["added_friends"])  )	#print number of friends

	
# Downloads every unopened snap
def download_new_snaps(user):
	all_snaps = user.get_snaps()
	new_snaps = []

	for snap in all_snaps:
		if snap['status'] == 1 and snap['id'][-1] == 'r':
			base_path = DOWNLOAD_PATH + snap['sender'] + "-" + str(datetime.datetime.now())
			file_path = user.download_media(snap['id'],  base_path)
			if file_path:
				snap['location'] = file_path
				snap['approved'] = SKIP_REVIEW
				snap['reviewed'] = False
				snap['uploaded'] = False
				new_snaps.append(snap)

	if len(new_snaps):
		PENDING_SNAPS_TABLE.insert(new_snaps)

def process_approved_snaps(user):
	for snap in PENDING_SNAPS_TABLE.find({'approved':True, 'uploaded':False}):
		media_id = user.upload(snap['media_type'], snap['location'])
		if media_id:
			if user.add_story(media_id, snap['media_type'], 5):
				PENDING_SNAPS_TABLE.update(snap, {"$set":{"uploaded":True}})
				if DELETE_MEDIA:
					os.remove(snap['location'])
				if DELETE_DATA:
					PENDING_SNAPS_TABLE.remove(snap["_id"])
			else:
				print "\nFailed To Post Snap To Story"
				print snap
		else:
			print "\nFailed To Upload Snap"
			print snap

def process_unapproved_snaps():
	for snap in PENDING_SNAPS_TABLE.find({'approved':False, 'reviewed':True}):
		if DELETE_MEDIA:
			os.remove(snap['location'])
		if DELETE_DATA:
			PENDING_SNAPS_TABLE.remove(snap)

def sleep_random():
	time.sleep(randint(MIN_SLEEP, MAX_SLEEP))



###########################
######## LOOP CODE ########
###########################
def main():
		try:
			os.makedirs(DOWNLOAD_PATH)
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

		for attempt in range(0,MAX_FAILURES):
			try:
				while True:
					#Loop is less fragile with a new session generated every iteration
					snap_user = Snapchat(USERNAME, PASSWORD)
					
					#Accept every new friend request
					accept_friend_requests(snap_user)
					
					#Download all new snaps
					download_new_snaps(snap_user)
					
					#Upload and potentially delete data
					process_approved_snaps(snap_user)

					#Potentially delete data
					process_unapproved_snaps()

					#Mark all snaps as read		
					snap_user.clear_feed()

					#Logout
					snap_user.logout()

					#Block the loop for a random number of seconds to avoid upsetting Snapchat
					sleep_random()
			except:
				print "\nEXECUTION ENDED IN ERROR\n"
				if attempt < MAX_FAILURES:
					print "Restarting AutoSnapper: %d Attempts Remaining\n" % (MAX_FAILURES - attempt - 1)
				else:
					print "Max Attempts Reached\n"
					raise
					

if __name__ == '__main__':
	main()
