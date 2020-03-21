const MongoClient = require('mongodb').MongoClient;
const async = require('async');


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


MongoClient.connect("mongodb://localhost:27017", {useNewUrlParser: true}, function (err, serverclient) {
    if (err) {
        console.log(err);
        // reject(err)
    } else {
        MongoClient.connect("mongodb://localhost:27017", {useNewUrlParser: true}, function (err, localclient) {
            if (err) {
                console.log(err);
                // reject(err)
            } else {
                const uninstall_users = localclient.db('uninstall_users');
                const way2db = localclient.db('way2db');

                uninstall_users.find({}).limit(1).toArray(function (err, docs) {
                    if (!err && docs) {
                        async.eachSeries(docs, function (doc, cb) {
                            let custid = doc.custid;
                            let inc_doc = {};
                            let dates = generateDates(30, 0);
                            let imp_events = ["full_img_ad_click", "full_img_ad_screenshot", "othershare", "removebookmark", "notification_clear", "whatsappshare", "videodownload", "whatsappshare", "twittershare", "messengershare", "number_posts_per_day", "likeclick_two"]
                            async.eachSeries(dates, function (date, dcb) {
                                let day = date.split("-")[2;
                                let month = date.split("-")[1];
                                let year = date.split("-")[0];
                                let today_post_times={};
                                way2db.collection("track_posts_cat_" + day + "_" + month + "_" + year).find({
                                    cust_id: custid
                                }).sort({time1: 1}).toArray(function (err, posts) {
                                    if (!err && posts) {
                                        let prev_post_time = new Date(posts[0].time1).getTime();
                                        let sess_start_time = prev_post_time;
                                        let sessions = 0;
                                        let total_posts = 0;
                                        let total_time_spent = 0;
                                        posts.splice(0, 1);
                                        async.eachSeries(posts, function (post, pcb) {
                                            today_post_times[post.postid]=post.time1;
                                            let curr_post_time = new Date(post.time1).getTime();
                                            total_posts++;
                                            if (curr_post_time - prev_post_time > 30 * 60 * 1000) {
                                                sessions++
                                                total_time_spent = total_time_spent + sess_start_time - prev_post_time;
                                                sess_start_time = curr_post_time;
                                                prev_post_time = curr_post_time;
                                            } else {
                                                prev_post_time = curr_post_time;
                                            }
                                            pcb();
                                        }, function () {
                                            let posts_per_session = total_posts / sessions;
                                            let time_spent_per_session = total_time_spent / sessions;

                                            inc_doc["tsps"] = time_spent_per_session;
                                            inc_doc["pps"] = posts_per_session;
                                            inc_doc["sessions"] = sessions;

                                            way2db.collection("posts_events_tracking_" + month + "_" + year).find({
                                                cust_id: custid,
                                                track_date: date
                                            }).toArray(function (err, events) {
                                                if (!err && events) {
                                                    events.forEach(function (event) {
                                                        if (imp_events.indexOf(event.con_type) > -1) {
                                                            if (inc_doc[event.con_type])
                                                                inc_doc[event.con_type] += 1;
                                                            else
                                                                inc_doc[event.con_type] = 1;
                                                        }
                                                    });
                                                    uninstall_users.updateOne({custid: custid}, {$inc: inc_doc}, function (err, ok) {
                                                        dcb();
                                                    })
                                                }
                                            })


                                        })

                                    }
                                })

                            }, function () {
                                cb()
                            })
                        }, function () {

                        })

                    }
                })

            }
        });


    }
});