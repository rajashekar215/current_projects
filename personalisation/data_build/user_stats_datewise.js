const MongoClient = require('mongodb').MongoClient;
const async = require('async');
const dateTime = require('node-datetime');
var moment = require("moment")
const mongo = require('mongodb');


function generateDates(totalDays, days) {
    if (totalDays) {
        if (days) {
            totalDays += 1;
        }
        const dayStamp = days ? days : Date.now();
        const today_conversion = new Date(dayStamp + 86400000);
        const today = new Date(Date.UTC(today_conversion.getFullYear(),
            today_conversion.getMonth(), today_conversion.getDate() - 1)).getTime() - (11 * 30 * 60 * 1000);
        // console.log("today",today);
        const oldDay = today - ((totalDays - 1) * 24 * 60 * 60 * 1000);
        let checkDay = oldDay;
        const dates = [];
        while (checkDay <= today) {
            dates.push(formatDate(checkDay));
            checkDay = checkDay + (24 * 60 * 60 * 1000);
        }
        // console.log('dates', dates);
        return dates;
    }
}
function formatDate(d) {
    this.date = new Date(d)
    var dd = this.date.getDate();
    var mm = this.date.getMonth() + 1;
    var yyyy = this.date.getFullYear();
    if (dd < 10) {
        dd = '0' + dd
    }
    if (mm < 10) {
        mm = '0' + mm
    }
    ;
    return d = yyyy + '-' + mm + '-' + dd;
}

var objectIdFromDate = function (date) {
    return Math.floor(date.getTime() / 1000).toString(16) + "0000000000000000";
};

function getDates(startDate, stopDate, last_post_time) {
    var dateArray = [];
    var currentDate = moment(startDate);
    var stopDate = moment(stopDate);
    while (currentDate <= stopDate) {
        dateArray.push({ date: moment(currentDate).format('YYYY-MM-DD'), time: last_post_time })
        last_post_time = "0"
        currentDate = moment(currentDate).add(1, 'days');
    }
    return dateArray;
}

function stats() {

    MongoClient.connect("mongodb://49.156.128.103:27017/way2?readPreference=secondaryPreferred", function (err, serverclient) {
        if (err) {
            console.log(err);
            // reject(err)
        } else {
            MongoClient.connect("mongodb://localhost:27017",  function (err, localclient) {
                if (err) {
                    console.log(err);
                    // reject(err)
                } else {
                    const localdb = localclient.db('way2_personalize_speed');
                    const way2db = serverclient.db('way2');

                    localdb.collection("testing_users").find({
                        // custid: 21118250,
                        stats: { $in: [0, null] }
                    }).limit(10).toArray(function (err, docs) {
                        if (!err && docs && docs.length) {
                            async.eachSeries(docs, function (doc, cb) {
                                let custid = doc.custid;
                                console.log("preparing stats for " + custid)
                                let inc_doc = {};
                                // let dates = generateDates(30, 0);
                                // let imp_events = ["full_img_ad_click", "full_img_ad_screenshot", "othershare", "removebookmark", "notification_clear", "whatsappshare", "videodownload", "whatsappshare", "twittershare", "messengershare", "number_posts_per_day", "likeclick_two"]

                                let today_date = dateTime.create().format('Y-m-d H:M:S').split(" ")[0]
                                // let today_date = "2019-09-16"
                                let last_post_date = doc.stats_last_post_date ? doc.stats_last_post_date : today_date
                                let last_post_time = doc.stats_last_post_time ? doc.stats_last_post_time : "0"
                                

                                let datesArr = []
                                console.log(last_post_date)
                                if (today_date != last_post_date) {
                                    datesArr = getDates(last_post_date, today_date, last_post_time)
                                } else {
                                    datesArr.push({ date: last_post_date, time: last_post_time })
                                }
                                console.log("dates:: ", datesArr)
                                let new_last_post_date = ""
                                let new_last_post_time = ""
                                let sum_tsps = 0
                                let sum_pps = 0
                                let sum_sessions = 0
                                let today_new_tsps = 0
                                let today_new_pps = 0
                                let today_new_sessions = 0
                                let total_dates = 0

                                async.forEachOf(datesArr, function (dateobj, dateindex, dcb) {
                                    let dst = Date.now();
                                    let date = dateobj.date;
                                    let time = dateobj.time;
                                    let datestring = date;
                                    if (time != "0") {
                                        let new_time=time.split(":")
                                        new_time[2]=parseInt(new_time[2])+1
                                        new_time=new_time.join(":")
                                        datestring += " " + new_time
                                    } else {
                                        if (dateindex != datesArr.length - 1) {
                                            total_dates += 1
                                        }
                                        datestring += " 00:00:00"
                                    }

                                    let day = date.split("-")[2].replace(/^0+/, '');;
                                    let month = date.split("-")[1].replace(/^0+/, '');;
                                    let year = date.split("-")[0];
                                    // let today_post_times={};
                                    console.log("track_posts_cat_" + day + "_" + month + "_" + year)
                                    way2db.collection("track_posts_cat_" + day + "_" + month + "_" + year).find({
                                        _id: { $gt: mongo.ObjectID(objectIdFromDate(new Date(datestring))) },
                                        custid: custid,
                                        cat_id: { $ne: 2 }
                                    }).sort({
                                        // time1: 1,
                                        _id: 1
                                    }).toArray(function (err, posts) {
                                        if (!err && posts && posts.length>0) {
                                            console.log("posts   ",posts)
                                            let sessions = 0;
                                            let total_posts = 1;
                                            let total_time_spent = 0;
                                            // posts.splice(0, 1);
                                            async.forEachOf(posts, function (post, index, pcb) {
                                                // today_post_times[post.postid]=post.time1;
                                                if (index != 0) {
                                                    let curr_post_time = (new Date(post.date1 + " " + post.time1).getTime())/1000;
                                                    let prev_post_time = (new Date(posts[index - 1].date1 + " " + posts[index - 1].time1).getTime())/1000;
                                                    let time_spent = curr_post_time - prev_post_time
                                                    // console.log(post["postid"], time_spent, curr_post_time, prev_post_time)
                                                    if (time_spent > 30 * 60) {
                                                        sessions++
                                                    } else {
                                                        total_posts++;
                                                        total_time_spent += time_spent;
                                                    }

                                                    
                                                }
                                                if (index == (posts.length - 1)) {
                                                    if (dateindex == (datesArr.length - 1)) {
                                                        new_last_post_date = date
                                                        new_last_post_time = post.time1
                                                    }
                                                }
                                                pcb();
                                            }, function () {
                                                if(posts.length != 0 && !sessions){
                                                    sessions=1
                                                }
                                                console.log("date ", date)
                                                console.log("total_posts:: ", total_posts)
                                                console.log("total_time_spent:: ", total_time_spent)
                                                console.log("sessions:: ", sessions)

                                                let posts_per_session = total_posts / sessions;
                                                let time_spent_per_session = total_time_spent / sessions;

                                                let today_new_tsps = time_spent_per_session
                                                let today_new_pps = posts_per_session
                                                let today_new_sessions = sessions
                                             
                                                localdb.collection("user_stats").findOne({date:date,custid:custid},function(err,stat_doc){
                                                    
                                                    if(stat_doc){
                                                        update_doc={}
                                                        let total_old_posts = stat_doc.total_posts ? stat_doc.total_posts : 0
                                                        let total_time_spent_old = stat_doc.total_time_spent ? stat_doc.total_time_spent : 0
                                                        let today_old_tsps = stat_doc.avg_tsps ? stat_doc.avg_tsps : 0
                                                        let today_old_pps = stat_doc.avg_pps ? stat_doc.avg_pps : 0
                                                        let today_old_sessions = stat_doc.sessions ? stat_doc.sessions : 0
                                                        
                                                        update_doc["total_posts"] = total_posts + total_old_posts
                                                        update_doc["total_time_spent"] = total_time_spent + total_time_spent_old
                                                        update_doc["avg_tsps"] = ((today_old_tsps * today_old_sessions) + (today_new_tsps * today_new_sessions)) / today_old_sessions + today_new_sessions
                                                        update_doc["avg_pps"] = ((today_old_pps * today_old_sessions) + (today_new_pps * today_new_sessions)) / today_old_sessions + today_new_sessions
                                                        update_doc["sessions"] = today_old_sessions + today_new_sessions

                                                        localdb.collection("user_stats").updateOne({custid:custid,date:date},{$set:update_doc},function(err,ok){
                                                            dcb();
                                                        })
                                                    }else{
                                                        insert_doc={custid:custid,date:date}
                                                        insert_doc["total_posts"] = total_posts 
                                                        insert_doc["total_time_spent"] = total_time_spent
                                                        insert_doc["avg_tsps"] = today_new_tsps
                                                        insert_doc["avg_pps"] = today_new_pps
                                                        insert_doc["sessions"] = today_new_sessions
                                                        localdb.collection("user_stats").insertOne(insert_doc,function(err,ok){
                                                            dcb();
                                                        })
                                                    }
                                                   
                                                })
                                               

                                            })

                                        } else {
                                            if (!err && posts.length == 0) {
                                                console.log("no posts seen on " + date,dateindex,datesArr.length)
                                                if (dateindex == (datesArr.length - 1)) {
                                                    new_last_post_date = date
                                                    new_last_post_time = "0"
                                                }
                                                localdb.collection("user_stats").findOne({date:date,custid:custid},function(err,stat_doc){
                                                    
                                                    if(!stat_doc){
                                                        insert_doc={custid:custid,date:date}
                                                        insert_doc["total_posts"] = 0 
                                                        insert_doc["total_time_spent"] = 0
                                                        insert_doc["avg_tsps"] = 0
                                                        insert_doc["avg_pps"] = 0
                                                        insert_doc["sessions"] = 0
                                                        localdb.collection("user_stats").insertOne(insert_doc,function(err,ok){
                                                            dcb();
                                                        })
                                                    }else{
                                                        dcb();
                                                    }
                                                   
                                                })
                                                // dcb();
                                            } else {
                                                console.log(err)
                                                process.exit(0)
                                            }
                                        }
                                    })

                                }, function () {
                                    update_doc = {stats:1}
                                    if(!(datesArr.length==1 && datesArr[0].date==new_last_post_date && new_last_post_time=="0")) {
                                        update_doc["stats_last_post_date"] = new_last_post_date
                                        update_doc["stats_last_post_time"] = new_last_post_time
                                    }
                                   
                                    console.log("new last post date ", new_last_post_date)
                                    // console.log("update document ", update_doc)
                                    // cb()
                                    localdb.collection("testing_users").updateOne({custid: custid}, {$set: update_doc}, function (err, ok) {
                                        console.log("updated stats for "+custid)
                                            cb();
                                        })
                                })
                            }, function () {
                                localclient.close()
                                serverclient.close()
                                console.log("**********all custids completed***********")
                                // setTimeout(stats,0)
                            })

                        }else{
                            console.log("no testing custids found")
                            localdb.collection("testing_users").updateMany({}, { $set: { stats:0} }, { upsert: true }, function (err, success) {
                                // db.close();
                                if (!err) {
                                    console.log("all custids updated")
                                    setTimeout(stats, 0);
                                } else {
                                    console.log(err);
                                }
                            })
                        }
                    })

                }
            });


        }
    });
}

stats()