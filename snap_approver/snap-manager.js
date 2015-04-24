var DB = require('mongodb'),
	MongoClient = DB.MongoClient,
	ObjectId = DB.ObjectID;

var SnapManager = function(callback) {
	MongoClient.connect('mongodb://localhost:27017/autosnapper', function(err, db){
		if(err) {
			console.log("ERROR: Failed To Connect To Mongo Instance");
			throw err;
		} 
		console.log("Snap Manager Connected To Mongo")

		var PendingSnaps = db.collection('pending_snaps');
		var client = {};

		client.approveSnap = function(id, approved) {
			PendingSnaps.update(
					{"_id": new ObjectId(id)},
					{$set:{"approved":approved, "reviewed":true}}, 
					{upsert:true, w: 1}, 
					function(err, result) {
	      				if(err) throw err;
	      				console.log("Snap Reviewed");
	      				console.log("Approved: " + approved);
	      				console.log(result);
	      			}
	      	);
		};

		client.pathForSnap = function(id, callback) {
			PendingSnaps.findOne({"_id": new ObjectId(id)}, function(err, snap){
				if(err) throw err;
				if(snap) {
					console.log("Snap Path Requested: " + snap["location"]);
					callback(snap["location"]);
				}
				else {
					console.log("Snap Path Requested Failed");
					console.log("Invalid ID: " + id);
					callback(null);
				}
			});
		};
		
		client.popSnapID = function(callback) {
			PendingSnaps.findOne({"reviewed":false}, function(err, snap){
				if(err) throw err;
				if (snap) {
					console.log("Popped Snap");
					console.log(snap)
					var media_type = "image";
					if(snap["media_type"] == 1) {
						media_type = "video"
					}
					callback(snap["_id"].toString(), media_type);	
				}
				else {
					console.log("No Snaps Need Reviewing")
					callback(null);
				}
				
			});
		};
		callback(client);
	});
}; 

module.exports = SnapManager;