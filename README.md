# autosnapper
Powered by Node.js, MongoDB, and Python
Responsive Web App that downloads all your SnapChats, lets you archive them, and automatically repost to your story 

Several "Celebrity" Snapchat accounts have become quite popular recently by reposting the Snapchats they recieve to their story,
creating a newsfeed of sorts.  

For Example: 
- http://totalfratmove.com/new-snapchat-account-documenting-debauchery-at-arizona-state-is-blowing-up/
- http://college.usatoday.com/2015/02/21/college-specific-snapchat-stories-stir-legal-concerns/
- iastate_snaps reportedly gained nearly 17,000 viewers
- hokie_snaps reportedly gained over 10,000 viewers

These accounts are usually operated by individuals manually downloading and reuploading Snaps using third-party apps.
This app eliminates the need for third-party apps and creates an automated platform for this type of SnapChat user.

#How It Works
- autosnapper/autosnapper.py is responsible for downloading all recieved Snaps and storing metadata in MongoDB
- snap_approver/app.js is a webserver responsible for a one-page Web App that displays the recently received Snaps
- The Web App displays the Snap Image or Video and gives the account admin the option to approve or veto the Snap.  Once a decision is made the Server updates the Snaps data in Mongo.  If the Snap is approved the autosnapper will then post it to the user's story!

![alt tag](https://raw.github.com/tophep/SnapHack-Framework/master/snap_approver/SnapApprover.png)


#How To Run It

- Install python, python-dev, python-pip, node, npm, and MongoDB
- sudo pip install Pillow
- sudo pip install pycrypto
- sudo pip install pymongo
- sudo mongod
- sudo python autosnapper/autosnapper.py
- cd snap_approver
- sudo npm install
- sudo node app.js
