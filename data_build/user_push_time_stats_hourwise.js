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


MongoClient.connect("mongodb://192.168.1.99:27017/way2?readPreference=secondaryPreferred", function (err, serverdb) {

MongoClient.connect("mongodb://localhost:27017/way2_push", function (err, localdb) {


function get_post_data(table_name,start,end,maxSno,pcb){
    let q="select custid,hour(from_unixtime(clicked_date)) as hour,DAYNAME(from_unixtime(clicked_date)) as day,post_id   FROM "+table_name+" WHERE sno BETWEEN "+start+" AND "+end+" group by custid,post_id;"
    console.log(q)
    pool.getConnection(function(err, connection) {
        connection.query( q, function(err, rows) {
            connection.release();
             console.log("got response")
            async.forEach(rows,function(doc,acb){
                localdb.collection("push_stats_hourwise").updateOne(
                    {"custid":doc["custid"]}
                    ,{"$inc":{[doc.hour]:1,"total_opens":1}}
                    ,{upsert:true},function(){
                        acb(doc["day"])
                    })
            },function(day){
                console.log(day)
                if(end+1000<maxSno){
                    get_post_data(table_name,end+1,end+1000,maxSno,function(){
                        pcb(day)
                    })
                }else if(end!=maxSno){
                    get_post_data(table_name,end+1,maxSno,maxSno,function(){
                        pcb(day)
                    })
                }else{
                    pcb(day)
                }      
                // pcb(day)         
            })
        });
    });
    
}

function get_push_counts(day,today_date,pushcb){
    let table_name='push_notification_tracking_'+today_date.split("-")[1]+'_'+today_date.split("-")[0]
    localdb.collection("push_stats_hourwise").find({"day":day,"cstats":0}).limit(1000).toArray(function(err,docs){
        if(docs && docs.length>0){
            console.log(today_date,table_name,docs.length)
            async.forEach(docs,function(user,apcb){
                serverdb.collection(table_name).aggregate([
                    {"$match":{"cust_id":user["custid"],"track_date":today_date}}
                    ,{"$group":{"_id":"$cust_id","langid":{"$first":"$lang_id"},"count":{"$sum":"$delivered"}}}
                ]).toArray(function(err,res){
                    // console.log(user["custid"],today_date,res)
                    if(res && res[0] && res[0].count){
                        localdb.collection("push_stats_hourwise").findOne({"custid":user["custid"],"day":day},function(err,crec){
                            let new_total_opens=crec["total_opens"]?crec["total_opens"]:0
                            let new_total_pushes=crec["total_pushes"]?crec["total_pushes"]+res[0]["count"]:res[0]["count"]
                            let push_open_rate=(new_total_opens/new_total_pushes)*100
                            let langid=res[0]["langid"] 
                            localdb.collection("push_stats_hourwise").updateOne(
                                {"custid":user["custid"],"day":day}
                                ,{"$set":{"total_pushes":new_total_pushes,"push_open_rate":push_open_rate.toFixed(2),"cstats":1,"langid":langid}}
                                ,{upsert:true}
                                ,function(){
                                    apcb()
                            })
                        })
                    }else{
                        localdb.collection("push_stats_hourwise").updateOne(
                            {"custid":user["custid"],"day":day}
                            ,{"$set":{"cstats":1}}
                            ,{upsert:true}
                            ,function(){
                                apcb()
                        })
                    }
                })
            },function(){
                get_push_counts(day,today_date,function(){
                    pushcb()
                })
            })
        }else{
            pushcb()
        }
    })
}


function get_user_stats(minSno,from_time,to_time,end_time,cb){
    let tdate=moment(from_time*1000).format("YYYY-MM-DD")
    let table_name="push_share_opens_"+tdate.split("-")[1].replace(/^0+/, '')+"_"+tdate.split("-")[0]
    console.log(tdate,table_name)
    let q="select MIN(sno) minSno, MAX(sno) maxSno FROM "+table_name+" WHERE clicked_date BETWEEN "+from_time+" AND "+(to_time-1)
    console.log(q)
    pool.getConnection(function(err, connection) {
        connection.query( q, function(err, rows) {
            connection.release();
            console.log(err,rows)
	    if(!minSno){
		minSno=rows[0]["minSno"]
		}
            let maxSno=rows[0]["maxSno"]
            get_post_data(table_name,minSno,minSno+1000,maxSno,function(day){
                console.log("step1")
                //setTimeout(get_pnids,0)
                if(to_time+86400<end_time){
                    get_user_stats(null,to_time,to_time+86400,end_time,function(){
                        cb()
                    })
                }else{
                    cb()
                }
          })
        });
    });

}


function get_pnids(){
    localdb.collection("push_stats_hourwise").find({pnid:null}).limit(1000).toArray(function(err,docs){
	if(docs && docs.length){
        async.forEach(docs,function(doc,cb){
            let q="select * FROM user_pnids WHERE custid="+doc["custid"]
            console.log(q)
            pool.getConnection(function(err, connection) {
                connection.query( q, function(err, row) {
                    connection.release();
		    //console.log(q,row)
                    localdb.collection("push_stats_hourwise").updateOne({
                        custid:doc["custid"]},
                        {$set:row[0]},function(){
                            cb();
                        })
                })
            })

        },function(){
		setTimeout(get_pnids,0)
        })
	}else{
		console.log("pnids fetched")
		//console.timeEnd();
	}
    })
}
//console.time()
//get_pnids()
// console.time();

let start_date="2019-12-31"
let end_date="2020-01-08"
let start_time=(dateTime.create(start_date+" 00:00:00").now())/1000
let end_time=(dateTime.create(end_date+" 00:00:00").now())/1000
let minSno=null
get_user_stats(minSno,start_time,start_time+86400,end_time,function(){
   // console.timeEnd();
    })

// function update_stats(start_time,end_time){
//     get_user_stats(start_time,start_time+86400,end_time,function(){
//         update_stats(end_time,end_time+86400)
//     })
// } 

 
// let start_date=moment().subtract(1, 'days').format("YYYY-MM-DD")
// let end_date=moment().format("YYYY-MM-DD")
// let start_time=(dateTime.create(start_date+" 00:00:00").now())/1000
// let end_time=(dateTime.create(end_date+" 00:00:00").now())/1000
// update_stats(start_time,end_time)
    
    


})

})
