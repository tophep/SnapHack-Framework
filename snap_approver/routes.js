var express = require('express');
var router = express.Router();
var fs = require('fs');

router.get('/pop', function(req, res, next) {
  req.snapclient.popSnapID(function(id, media_type){
  	if(id) {
  		console.log("SENDING ID: " + id);
  		res.send(media_type + id);	
  	}
  	else {
  		res.send(null);
  	}
  });
  
});

router.get('/snaps/:id', function(req, res, next) {
	req.snapclient.pathForSnap(req.params.id, function(path){
		if(path){
			res.sendFile(path);	
		}
		else {
			res.send(null);
		}
	});
});

router.post("/snaps/:id/:approved", function(req, res, next) {
	var id = req.params.id;
	var approved = req.params.approved;
	if(approved == "true") {
		approved = true;
	}
	else {
		approved = false;
	}
	req.snapclient.approveSnap(id, approved);
	res.end();
});


module.exports = router;
