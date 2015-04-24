import requests
import hashlib
import json
import time
import uuid
from StringIO import StringIO
from PIL import Image

from datetime import datetime
from Crypto.Cipher import AES


class Snapchat(object):
    URL =                       'https://feelinsonice-hrd.appspot.com/'
    GENERAL_PATH_EXTENSION =    'bq'
    LOGIN_PATH_EXTENSION =      'loq'
    SEND_PATH_EXTENSION =       'ph'
    SECRET =                    'iEk21fuwZApXlz93750dmW22pw389dPwOk'        # API Secret
    STATIC_TOKEN =              'm198sOkJEn37DjqZ32lpRu76xmw288xSQ9'        # API Static Token
    BLOB_ENCRYPTION_KEY =       'M02cnQ51Ji97vwT4'                          # Blob Encryption Key
    HASH_PATTERN =              '0001110111101110001111010101111011010001001110011000110001000110'; # Hash pattern
    HEADERS = {
                                'User-Agent':'Snapchat/9.6.0 (iPhone; iOS 9.6.0; gzip)',
                                'Accept-Language':'en',
                                'Accept-Locale':'en_US'
    }
    SNAPCHAT_VERSION =          '9.6.0'                                     # Snapchat Application Version

    MEDIA_IMAGE =                        0  # Media: Image
    MEDIA_VIDEO =                        1  # Media: Video
    MEDIA_VIDEO_NOAUDIO =                2  # Media: Video without audio
    MEDIA_FRIEND_REQUEST =               3  # Media: Friend Request
    MEDIA_FRIEND_REQUEST_IMAGE =         4  # Media: Image from unconfirmed friend
    MEDIA_FRIEND_REQUEST_VIDEO =         5  # Media: Video from unconfirmed friend
    MEDIA_FRIEND_REQUEST_VIDEO_NOAUDIO = 6  # Media: Video without audio from unconfirmed friend

    STATUS_NONE =                       -1  # Snap status: None
    STATUS_SENT =                        0  # Snap status: Sent
    STATUS_DELIVERED =                   1  # Snap status: Delivered
    STATUS_OPENED =                      2  # Snap status: Opened
    STATUS_SCREENSHOT =                  3  # Snap status: Screenshot

    FRIEND_CONFIRMED =                   0  # Friend status: Confirmed
    FRIEND_UNCONFIRMED =                 1  # Friend status: Unconfirmed
    FRIEND_BLOCKED =                     2  # Friend status: Blocked
    FRIEND_DELETED =                     3  # Friend status: Deleted

    PRIVACY_EVERYONE =                   0  # Privacy setting: Accept snaps from everyone
    PRIVACY_FRIENDS =                    1  # Privacy setting: Accept snaps only from friends

    # Optionally log in during initialization 
    def __init__(self, username=None, password=None):
        self.username = None
        self.auth_token = None
        self.logged_in = False

        # Generate a cipher for encrypting/decrypting media files
        self.cipher = AES.new(Snapchat.BLOB_ENCRYPTION_KEY, AES.MODE_ECB)

        if username and password:
            self.login(username, password)

########################################
######## WORKING CLIENT METHODS ########
########################################

    # Attempts to register a new user with the specified information
    def register(self, username, password, email, birthday):
        # birthday should be a string of form "yyyy-mm-dd"

        data = {
            'birthday': birthday,
            'password': password,
            'email': email
        }

        # Perform email/password registration.
        result = self._post('/register', data, Snapchat.STATIC_TOKEN)

        if 'auth_token' in result:
            self.auth_token = result["auth_token"]
            self.username = username
            self.logged_in = True
            print "Registration Successful For User: " + username + "\n"
            return True
        else:
            print "Registration Failed For User: " + username
            print "With Error:\n"
            print result
            return False

    # Attempts to login using the specified credentials
    def login(self, username, password):

        if self.logged_in:
            return True

        data = {
            'username': username,
            'password': password
        }

        result = self._post('/login', data, Snapchat.STATIC_TOKEN)
        try: 
            if 'auth_token' in result and 'username' in result:
                self.logged_in = True
                self.username = result['username']
                self.auth_token = result['auth_token']
                print "Login Successful\n"
                return True
            else:
                print "Login Failed"
                print "With Error:\n"
                print result
                return False      
        except:
            print "No JSON Returned"
            print "Login Failed"
            print "With Error:\n"
            print result
            return False
        


    # Attempts to logout of the current session
    def logout(self):

        if not self.logged_in:
            return True

        data = {
            'username': self.username
        }

        result = self._post('/logout', data, self.auth_token)
        if result:
            print "Logout Unsuccessful"
            print "With Error:\n"
            print result
            return False
        else:
            self.logged_in = False
            self.username = None
            self.auth_token = None
            print "Logout Successful\n"
            return True


    # Attempts to upload a file to the Snapchat servers
    def upload(self, media_type, filename):
        # Use a predefined media type, i.e. Snapchat.MEDIA_IMAGE
        # Use the full file path (including extension)
        # Upon successful upload, the file can be sent to a user by calling send

        if not self.logged_in: raise Exception("No User Logged In")

        # Before being sent to another user, Snaps are identified by media_id
        media_id = self.username.upper() + '~' + str(uuid.uuid4())

        data = {
            'media_id': media_id,
            'type': media_type,
            'username': self.username
        }

        encrypted_media = self._encrypt_media(filename)

        result = self._post('/upload', data, self.auth_token, encrypted_media)
        if result:
            print "Upload Unsuccessful"
            print "With Error:\n"
            print result
            return False
        else:
            print "Upload Successful\n"
            return media_id


    # Sends a previously uploaded media file to the specified users
    def send(self, media_id, media_type, recipients, time=10):
        # Call upload to get a media_id
        # recipients: the recipients username as a string (single recipient) or list of strings (multiple recipients)
        # time: allotted viewing time for image

        if not self.logged_in: raise Exception("No User Logged In")

        # If only one recipient, convert it to a list.
        if not isinstance(recipients, list):
            recipients = [recipients]

        data = {
            'media_id': media_id,
            'recipient': ','.join(recipients),
            'time': time,
            'username': self.username,
            'type':media_type
        }

        result = self._post('/send', data, self.auth_token)
        if result:
            print "Sending Snap Failed"
            print "With Error:"
            print result
            return False
        else:
            print "Sending Snap Succeeded\n"
            return True


    # Adds a previously uploaded media file to the logged in user's story
    def add_story(self, media_id, media_type, time=10):
        # Call upload to get a media_id
        # time: allotted viewing time for image

        if not self.logged_in: raise Exception("No User Logged In")

        data = {
            'client_id': media_id,
            'media_id': media_id,
            'time': time,
            'username': self.username,
            'type': media_type
        }

        result = self._post('/post_story', data, self.auth_token)
        
        if isinstance(result, dict): 
            print "Add Story Successful\n"
            return True
        else:
            print "Add Story Failed"
            print "With Error:\n"
            print result
            return False


    # Returns giant list of meta-data pertaining to the user
    def get_updates(self):

        if not self.logged_in: raise Exception("No User Logged In")

        data = {
            'username': self.username
        }

        result = self._post('/all_updates', data, self.auth_token)
        if isinstance(result, dict): 
            print "Update Request Successful\n"
            return result
        else:
            print "Update Request Failed"
            print "With Error:\n"
            print result
            return False


    # Returns meta-data pertaining to the user's recent snaps (sent and received)
    def get_snaps(self):

        updates = self.get_updates()

        if not updates:
            print "Snap Data Request Failed"
            return False

        snaps = updates['updates_response']['snaps']
        result = []

        for snap in snaps:
            # Make the fields more readable.
            snap_readable = {
                'id': self._parse_field(snap, 'id'),
                'media_id': self._parse_field(snap, 'c_id'),
                'media_type': self._parse_field(snap, 'm'),
                'time': self._parse_field(snap, 't'),
                'sender': self._parse_field(snap, 'sn'),
                'recipient': self._parse_field(snap, 'rp'),
                'status': self._parse_field(snap, 'st'),
                'screenshot_count': self._parse_field(snap, 'c'),
                'sent': self._parse_datetime(snap['sts']),
                'opened': self._parse_datetime(snap['ts'])
            }
            result.append(snap_readable)

        print "Snap Data Request Successful\n"
        return result


    # Returns meta-data pertaining to the user's, and their friends', stories
    def get_stories(self):

        if not self.logged_in: raise Exception("No User Logged In")

        data = {
            'username': self.username
        }

        result = self._post('/stories', data, self.auth_token)

        if isinstance(result, dict): 
            print "Story Data Request Successful\n"
            return result
        else:
            print "Story Data Request Failed"
            print "With Error:\n"
            print result
            return False


    # Downloads and saves the requested media locally
    def download_media(self, id, filename_base):
        # id (not media_id) can be found by calling get_snaps or get_stories
        # Use the base file path (no extension)
        # Returns the full name of the saved file, False if there was an error
        return self._save_media(self.get_media(id), filename_base)


    # Returns the requested media in a raw byte string
    def get_media(self, id):
        # id (not media_id) can be found by calling get_snaps or get_stories

        if not self.logged_in: raise Exception("No User Logged In")

        data = {
            'id': id,
            'username': self.username
        }

        result = self._post('/blob', data, self.auth_token)
        return self._decrypt_media(result)
        

    # Sends a friend request to the user specified
    def add_friend(self, friend):

        if not self.logged_in: raise Exception("No User Logged In")

        data = {
            'action': 'add',
            'friend': friend,
            'username': self.username
        }

        self._post('/friend', data, self.auth_token)

        return True

    # Accepts all unanswered friend requests
    def accept_all_friend_requests(self):
        updates = self.get_updates()
        if updates:
            friends = updates["updates_response"]["added_friends"] #all users that every added you   
            for friend in friends:                      
                if friend["type"] == FRIEND_UNCONFIRMED:        
                    self.add_friend(friend["name"])                                  


    # Clears user's feed (list of previously opened snaps will be gone in-app)
    def clear_feed(self):
      
        if not self.logged_in: raise Exception("No User Logged In")

        data = {
            'username': self.username
        }

        result = self._post('/clear', data, self.auth_token)

        if result:
            print "Failed To Clear Feed\n"
            print "With Error:"
            print result
            return False
        else:
            print "Feed Clear Successful\n"
            return True


################################
######## HELPER METHODS ########
################################


    # Sends HTTP Post requests to the Snapchat Server
    def _post(self, endpoint, data, auth_token, media_data=None):
        # endpoint: The service to submit the request to, i.e. '/upload'.
        # data: Request data to upload, i.e. username, password, etc
        # auth_token: Either the STATIC_TOKEN, or the auth_token provided upon login
        # media_data: Optional field for submitting encrypted media file
    
        timestamp = self._timestamp()
        data['timestamp'] = timestamp
        data['req_token'] = self._hash(auth_token, timestamp)
        data['version'] = Snapchat.SNAPCHAT_VERSION

        extension = Snapchat.GENERAL_PATH_EXTENSION
        if endpoint == '/send':
            extension = Snapchat.SEND_PATH_EXTENSION
        elif endpoint == '/login':
            extension = Snapchat.LOGIN_PATH_EXTENSION

        url = Snapchat.URL + extension + endpoint

        if media_data:
            r = requests.post(url, data, headers=Snapchat.HEADERS, files={'data': media_data})
        else:
            r = requests.post(url, data, headers=Snapchat.HEADERS)

        # If the status code isn't 200, it's a failed request.
        if r.status_code != 200 and r.status_code != 202:
            print "Request for ", url, "Failed"
            print "Snapcht Server Response:", r.status_code
            print "With Error:"
            print r.content
        else:
            print "Request for ", url, " Successful"

        try:
            return json.loads(r.content)
        except:
            return r.content


    # Returns tokens used to validate requests on the server side and unlock the API
    def _hash(self, auth_token, timestamp):
        # This algorithm is a sneaky pattern Snapchat uses to generate request_tokens

        # Augment values with the Snapchat API SECRET 
        first = Snapchat.SECRET + str(auth_token).encode('utf-8')
        second = str(timestamp).encode('utf-8') + Snapchat.SECRET

        # Hash the values.
        hash1 = hashlib.sha256(first).hexdigest()
        hash2 = hashlib.sha256(second).hexdigest()

        # Using Snapchats secret bitmask, interleave the characters of the two hashes
        result = ''
        for pos, included in enumerate(Snapchat.HASH_PATTERN):
            if included == '0':
                result += hash1[pos]
            else:
                result += hash2[pos]

        return result


    # Returns the current time stamp in milliseconds
    def _timestamp(self):
        return int(time.time() * 1000)


    # Encrypts whole files, returns byte string
    def _encrypt_media(self, filename):
        with open(filename, 'rb') as f:
            return self._encrypt(f.read())


    # Encrypts binary data using the Snapchat cipher
    def _encrypt(self, data):
        data = self._pad(data)
        return self.cipher.encrypt(data)


    # Decrypts and saves whole files
    def _decrypt_media(self, data):
        if not self._is_media(data):
            data = self._decrypt(data)
            print "Media Decrypted"
            if not self._is_media(data):
                print "Unrecognizable File Format"
                print "Media Decryption May Have Failed"

        return data


    # Decrypts binary data using the Snapchat cipher
    def _decrypt(self, data):
        data = self._pad(data)
        return self.cipher.decrypt(data)


    # Pads data using PKCS5
    def _pad(self, data, blocksize=16):
        pad = blocksize - (len(data) % blocksize)
        return data + (chr(pad) * pad).encode('utf-8')


    # Saves decrypted byte string to a file
    def _save_media(self, data, filename_base):
        extension = self._is_media(data)
        if extension:
            file_path = filename_base + "." + extension
            if extension == "jpg":
                Image.open(StringIO(data)).save(file_path)
            else:
                with open(file_path, 'wb') as f:
                    f.write(data)
            print "Media Saved To:", file_path, "\n"
            return file_path
        else:
            print "Media Was Not Saved\n"
            return False        


    # Determines file type of media byte string
    def _is_media(self, data):
        # Check for JPG header.
        if data[0] == chr(0xff) and data[1] == chr(0xd8):
            return 'jpg'

        # Check for MP4/MOV header.
        if data[0] == chr(0x00) and data[1] == chr(0x00):
            return 'mp4'

        return False


    # Parses JSON data, takes care of ommitted and boolean fields 
    def _parse_field(self, dictionary, key, bool=False):

        if key not in dictionary:
            if bool:
                return False
            else: 
                return None

        return dictionary[key]


    def _parse_datetime(self, dt):

        try:
            return datetime.fromtimestamp(dt / 1000)
        except:
            return dt


#######################################
######## BROKEN CLIENT METHODS ########
#######################################


    def find_friends(self, numbers, country='US'):
        """Finds friends based on phone numbers.

        :param numbers: A list of phone numbers.
        :param country: The country code (US is default).
        :returns: List of user objects found.
        """

        if not self.logged_in: raise Exception("No User Logged In")

        # If only one recipient, convert it to a list.
        if not isinstance(numbers, list):
            numbers = [numbers]

        data = {
            'countryCode': country,
            'numbers': json.dumps(numbers),
            'username': self.username
        }

        result = self._post('/find_friends', data, self.auth_token)

        print result

        if 'results' in result:
            return result['results']

        return result


        