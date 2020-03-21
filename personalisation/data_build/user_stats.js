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

function stats(){

MongoClient.connect("mongodb://49.156.128.102:27017/way2?readPreference=secondaryPreferred", {useNewUrlParser: true}, function (err, serverclient) {
    if (err) {
        console.log(err);
        // reject(err)
    } else {
        MongoClient.connect("mongodb://localhost:27017", {useNewUrlParser: true}, function (err, localclient) {
            if (err) {
                console.log(err);
                // reject(err)
            } else {
                const localdb = localclient.db('way2_personalize_speed');
                const way2db = serverclient.db('way2');

                localdb.collection("user_stats").find({
                    custid:22172222,
                    stats: { $in: [0, null] } 
                }).limit(1).toArray(function (err, docs) {
                    if (!err && docs) {
                        async.eachSeries(docs, function (doc, cb) {
                            let custid = doc.custid;
                            console.log("preparing stats for "+custid)
                            let inc_doc = {};
                            // let dates = generateDates(30, 0);
                            // let imp_events = ["full_img_ad_click", "full_img_ad_screenshot", "othershare", "removebookmark", "notification_clear", "whatsappshare", "videodownload", "whatsappshare", "twittershare", "messengershare", "number_posts_per_day", "likeclick_two"]
                            
                            let today_date = dateTime.create().format('Y-m-d H:M:S').split(" ")[0]
                            // let today_date = "2019-09-16"
                            let last_post_date = doc.stats_last_post_date ? doc.stats_last_post_date : today_date
                            let last_post_time = doc.stats_last_post_time ? doc.stats_last_post_time : "0"
                            let avg_tsps=doc.avg_tsps ? doc.avg_tsps : 0
                            let avg_pps=doc.avg_pps ? doc.avg_pps : 0
                            let avg_sessions=doc.avg_sessions ? doc.avg_sessions : 0

                            let today_old_tsps=doc.today_tsps ? doc.today_tsps : 0
                            let today_old_pps=doc.today_pps ? doc.today_pps : 0
                            let today_old_sessions=doc.today_sessions ? doc.today_sessions : 0

                            let totaldays=doc.total_days?doc.total_days:0

                            let datesArr = []
                            console.log(last_post_date)
                            if (today_date != last_post_date) {
                                datesArr = getDates(last_post_date, today_date, last_post_time)
                            } else {
                                datesArr.push({ date: last_post_date, time: last_post_time })
                            }
                            console.log("dates:: ",datesArr)
                            let new_last_post_date = ""
                            let new_last_post_time = ""
                            let sum_tsps=0
                            let sum_pps=0
                            let sum_sessions=0
                            let today_new_tsps=0
                            let today_new_pps=0
                            let today_new_sessions=0
                            let total_dates=0

                            async.forEachOf(datesArr, function (dateobj,dateindex, dcb) {
                                let dst = Date.now();
                                let date = dateobj.date;
                                let time = dateobj.time;
                                let datestring = date;
                                if (time != "0") {
                                  datestring += " " + time
                                } else {
                                    if(dateindex!=datesArr.length-1){
                                        total_dates+=1     
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
                                    _id:1
                                }).toArray(function (err, posts) {
                                    if (!err && posts) {
                                        
                                        let sessions = 0;
                                        let total_posts = 0;
                                        let total_time_spent = 0;
                                        // posts.splice(0, 1);
                                        async.forEachOf(posts, function (post,index, pcb) 
                                        {
                                            // today_post_times[post.postid]=post.time1;
                                            if(index!=0){
                                                let curr_post_time = new Date(post.date1 + " " + post.time1).getTime();
                                                let prev_post_time = new Date(posts[index-1].date1 + " " + posts[index-1].time1).getTime();
                                                let time_spent=curr_post_time - prev_post_time
                                                console.log(post["postid"],time_spent,curr_post_time,prev_post_time)
                                                if (time_spent > 30 * 60 * 1000) {
                                                    sessions++
                                                } else {
                                                    total_posts++;
                                                    total_time_spent +=time_spent;
                                                }
    
                                                if (index == (posts.length - 1)) {
                                                    if(dateindex==(datesArr.length-1)){
                                                      new_last_post_date = date
                                                      new_last_post_time = post.time1
                                                    }
                                                }
                                            }
                                            pcb();
                                        }, function () {
                                            console.log("date ",date)
                                            console.log("total_posts:: ",total_posts)
                                            console.log("total_time_spent:: ",total_time_spent)
                                            console.log("sessions:: ",sessions)

                                            let posts_per_session = total_posts / sessions;
                                            let time_spent_per_session = total_time_spent / sessions;

                                            if(dateindex==(datesArr.length-1)){
                                                 today_new_tsps=time_spent_per_session
                                                 today_new_pps=posts_per_session
                                                 today_new_sessions=sessions
                                            }else{
                                                 sum_tsps+=time_spent_per_session
                                                 sum_pps+=posts_per_session
                                                 sum_sessions+=sessions
                                            }
                                           dcb()
                                            // way2db.collection("posts_events_tracking_" + month + "_" + year).find({
                                            //     cust_id: custid,
                                            //     track_date: date
                                            // }).toArray(function (err, events) {
                                            //     if (!err && events) {
                                            //         events.forEach(function (event) {
                                            //             if (imp_events.indexOf(event.con_type) > -1) {
                                            //                 if (inc_doc[event.con_type])
                                            //                     inc_doc[event.con_type] += 1;
                                            //                 else
                                            //                     inc_doc[event.con_type] = 1;
                                            //             }
                                            //         });
                                            //         uninstall_users.updateOne({custid: custid}, {$inc: inc_doc}, function (err, ok) {
                                            //             dcb();
                                            //         })
                                            //     }
                                            // })

                                        })

                                    }else{
                                        if(!err && posts.length==0){
                                            console.log("no posts seen on "+date)
                                            if(dateindex==(datesArr.length-1)){
                                                new_last_post_date = date
                                                new_last_post_time = "0"
                                              }
                                            dcb();
                                        }else{
                                            console.log(err)
                                            process.exit(0)
                                        }
                                    }
                                })

                            }, function () {
                                update_doc={}
                                update_doc["stats_last_post_date"]=new_last_post_date
                                update_doc["stats_last_post_time"]=new_last_post_time
                                console.log("new last post date ",new_last_post_date)
                                if(last_post_date==new_last_post_date){
                                    update_doc["today_tsps"]=((today_old_tsps*today_old_sessions)+(today_new_tsps*today_new_sessions))/today_old_sessions+today_new_sessions
                                    update_doc["today_pps"]=((today_old_pps*today_old_sessions)+(today_new_pps*today_new_sessions))/today_old_sessions+today_new_sessions
                                    update_doc["today_sessions"]=today_old_sessions+today_new_sessions
                                }else{
                                    update_doc["today_tsps"]=today_new_tsps
                                    update_doc["today_pps"]=today_new_pps
                                    update_doc["today_sessions"]=today_new_sessions

                                    let new_avg_tsps=0
                                    let new_avg_pps=0
                                    let new_avg_sessions=0
                                    
                                    let new_total_days=0
                                    if(today_old_tsps|today_old_pps|today_old_sessions){
                                        new_total_days=totaldays+total_dates+1
                                    }else{
                                        new_total_days=totaldays+total_dates
                                    }
                                    
                                    new_avg_tsps=((avg_tsps*totaldays)+today_old_tsps+sum_tsps)/new_total_days
                                    new_avg_pps=((avg_pps*totaldays)+today_old_pps+sum_pps)/new_total_days
                                    new_avg_sessions=((avg_sessions*totaldays)+today_old_sessions+sum_sessions)/new_total_days

                                    update_doc["avg_tsps"]=new_avg_tsps
                                    update_doc["avg_pps"]=new_avg_pps
                                    update_doc["avg_sessions"]=new_avg_sessions

                                    update_doc["total_days"]=new_total_days
                                }
                                console.log("update document ",update_doc)
                               cb()
                                // localdb.collection("user_stats").updateOne({custid: custid}, {$set: update_doc}, function (err, ok) {
                                //     console.log("updated stats for "+custid)
                                //         cb();
                                //     })
                            })
                        }, function () {
                            localclient.close()
                            serverclient.close()
                            console.log("**********all custids completed***********")
                            // setTimeout(stats,0)
                        })

                    }
                })

            }
        });


    }
});
}

stats()