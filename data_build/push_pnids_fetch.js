const async = require("async");
const mongo = require('mongodb');
const MongoClient = require('mongodb').MongoClient;
const config = require('./config/properties_r')
const poolsel = require('./dbconnection/dbsel');
const dateTime = require('node-datetime');
const moment = require("moment")


var mysql      = require('mysql');
var pool = mysql.createPool({
    host     : '192.168.1.98',
    user     : 'way2sms',
    password : 'waysmsawd#$%@',
    database: 'way2app'
});




MongoClient.connect("mongodb://localhost:27017/user_word_cloud", function (err, localdb) {

function get_pnids(){
    localdb.collection("november_active_users").find({pnid_status:null}).limit(1000).toArray(function(err,docs){
	if(docs && docs.length){
        async.forEach(docs,function(doc,cb){
		//console.log(doc)
            let q="select * FROM user_pnids WHERE custid="+doc["custid"]
            console.log(q)
            pool.getConnection(function(err, connection) {
                connection.query( q, function(err, row) {
                    connection.release();
		    //console.log(q,row)
                    if(row && row[0]){
			row[0]["pnid_status"]=1
			localdb.collection("november_active_users").updateOne({
                        custid:doc["custid"]},
                        {$set:row[0]},function(){
                            cb();
                        })
			}else{
			localdb.collection("november_active_users").updateOne({
                        custid:doc["custid"]},
                        {$set:{pnid_status:0}},function(){
                            cb();
                        })

			}
                })
            })

        },function(){
		setTimeout(get_pnids,1000)
        })
	}else{
		console.log("pnids fetched")
	}
    })
}
get_pnids()
    


})


