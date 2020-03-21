const MongoClient = require('mongodb').MongoClient;
const async = require('async');


function generateDates(totalDays, days) {
    if (totalDays) {
        // if (days) {
        //     totalDays += 1;
        // }
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
var data_collection="install_data_june_5";
var limit=100;
var time_group={tg1:[00,01,02,03,04,05],tg2:[06,07,08,09,10,11],tg3:[12,13,14,15,16,17],tg4:[18,19,20,21,22,23]};
MongoClient.connect("mongodb://49.156.128.103:27017", {useNewUrlParser: true}, function (err, serverclient) {
    if (err) {
        console.log(err);
        // reject(err)
    } else {
        MongoClient.connect("mongodb://localhost:27017", {useNewUrlParser: true}, function (err, localclient) {
            if (err) {
                console.log(err);
                // reject(err)
            } else {
                const way2_uninstall_data = localclient.db('way2_uninstall_data');
                const way2db = serverclient.db('way2');
                function getData() {
                    way2_uninstall_data.collection(data_collection).find({processed:null}).limit(limit).toArray(function (err, docs) {
                        if (!err && docs) {
                            console.log(docs.length);
                            async.each(docs, function (doc, cb) {
                                let custid = doc.custid;
                                // let dates = generateDates(2, 1561976323000);
                                let dates = generateDates(11, 1560567994000);
                                let imp_events = ["full_img_ad_click", "full_img_ad_screenshot", "othershare", "removebookmark", "notification_clear", "whatsappshare", "videodownload", "whatsappshare", "twittershare", "messengershare", "number_posts_per_day", "likeclick_two"]
                                async.each(dates, function (date, dcb) {
                                    console.log(date, custid)
                                    let day = date.split("-")[2].replace(/^0+/, '');
                                    let month = date.split("-")[1].replace(/^0+/, '');
                                    let year = date.split("-")[0];
                                    let today_post_times = {};
                                    let inc_doc = {};
                                    let field_doc = {};
                                    console.log("posts table--> ", "track_posts_cat_" + day + "_" + month + "_" + year)
                                    console.log("events table--> ", "posts_events_tracking_" + month + "_" + year)
                                    way2db.collection("track_posts_cat_" + day + "_" + month + "_" + year).find({
                                        custid: custid
                                    }).sort({_id: 1}).toArray(function (err, posts) {
                                        if (!err && posts && posts.length) {
                                            //let prev_post_time = new Date(posts[0].time1).getTime();
                                            //let sess_start_time = prev_post_time;
                                            //let sessions = 0;
                                            //let total_posts = 0;
                                            //let total_time_spent = 0;
                                            // posts.splice(0, 1);
                                            let prev_group = null;
                                            async.eachSeries(posts, function (post, pcb) {
                                                today_post_times[post.postid] = post.time1;
                                                let ptime = parseInt(post.time1.split(":")[0]);
                                                Object.keys(time_group).forEach(function (group) {
                                                    if (time_group[group].indexOf(ptime) > -1) {
                                                        let curr_post_time = new Date(post.date1 + " " + post.time1).getTime();
                                                        if (!field_doc[group]) {
                                                            field_doc[group] = {}
                                                        }
                                                        if (!prev_group) {
                                                            prev_group = group
                                                            field_doc[group].sessions = field_doc[group].sessions ? field_doc[group].sessions + 1 : 1;
                                                            field_doc[group].prev_post_time = curr_post_time;
                                                            field_doc[group].sess_start_time = curr_post_time;
                                                        } else {
                                                            if (prev_group != group) {
                                                                field_doc[prev_group].total_time_spent = field_doc[prev_group].total_time_spent ? field_doc[prev_group].total_time_spent + (field_doc[prev_group].prev_post_time - field_doc[prev_group].sess_start_time) : (field_doc[prev_group].prev_post_time - field_doc[prev_group].sess_start_time);
                                                                field_doc[group].sessions = field_doc[group].sessions ? field_doc[group].sessions + 1 : 1;
                                                                field_doc[group].sess_start_time = curr_post_time;
                                                                field_doc[group].prev_post_time = curr_post_time;
                                                            }
                                                            else if (field_doc[group].prev_post_time && curr_post_time - field_doc[group].prev_post_time > 30 * 60 * 1000) {
                                                                field_doc[prev_group].total_time_spent = field_doc[prev_group].total_time_spent ? field_doc[prev_group].total_time_spent + (field_doc[prev_group].prev_post_time - field_doc[prev_group].sess_start_time) : (field_doc[prev_group].prev_post_time - field_doc[prev_group].sess_start_time);
                                                                field_doc[group].sessions = field_doc[group].sessions ? field_doc[group].sessions + 1 : 1;
                                                                field_doc[group].sess_start_time = curr_post_time;
                                                                field_doc[group].prev_post_time = curr_post_time;
                                                            } else {
                                                                field_doc[group].prev_post_time = curr_post_time;
                                                            }
                                                            prev_group = group
                                                        }


                                                        // console.log("curr_post_time--",post.time1)

                                                        field_doc[group].total_posts = field_doc[group].total_posts ? field_doc[group].total_posts + 1 : 1;
                                                    }
                                                });
                                                pcb();
                                            }, function () {
                                                field_doc[prev_group].total_time_spent = field_doc[prev_group].total_time_spent ? field_doc[prev_group].total_time_spent + (field_doc[prev_group].prev_post_time - field_doc[prev_group].sess_start_time) : (field_doc[prev_group].prev_post_time - field_doc[prev_group].sess_start_time);
                                                console.log("field doc  " + JSON.stringify(field_doc))
                                                Object.keys(field_doc).forEach(function (group) {
                                                    let posts_per_session = Math.floor(field_doc[group].total_posts / field_doc[group].sessions);
                                                    let time_spent_per_session = Math.floor(field_doc[group].total_time_spent / field_doc[group].sessions);

                                                    inc_doc[group + "_tsps"] = time_spent_per_session / 1000;
                                                    inc_doc[group + "_pps"] = posts_per_session;
                                                    inc_doc[group + "_sessions"] = field_doc[group].sessions;
                                                });


                                                way2db.collection("posts_events_tracking_" + month + "_" + year).find({
                                                    cust_id: custid,
                                                    track_date: date
                                                }).toArray(function (err, events) {
                                                    if (!err && events) {
                                                        events.forEach(function (event) {
                                                            // console.log(event.post_id,today_post_times)
                                                            if (imp_events.indexOf(event.con_type) > -1) {
                                                                inc_doc[event.con_type] = inc_doc[event.con_type] ? inc_doc[event.con_type] + 1 : 1;
                                                                // if (event.con_type != "removebookmark" && event.con_type != "notification_clear") {
                                                                //     let etime = today_post_times[event.post_id.toString()];
                                                                //     console.log(event.post_id,today_post_times,date)
                                                                //     Object.keys(time_group).forEach(function (group) {
                                                                //         if (time_group[group].indexOf(parseInt(etime.split(":")[0])) > -1) {
                                                                //             inc_doc[group + "_" + event.con_type] = inc_doc[group + "_" + event.con_type] ? inc_doc[group + "_" + event.con_type] + 1 : 1;
                                                                //         }
                                                                //     });
                                                                // } else {
                                                                //     inc_doc[event.con_type] = inc_doc[event.con_type] ? inc_doc[event.con_type] + 1 : 1;
                                                                // }

                                                            }
                                                        });
                                                        console.log(date, inc_doc);
                                                        way2_uninstall_data.collection(data_collection).updateMany({custid: custid}, {$inc: inc_doc}, function (err, ok) {
                                                            dcb();
                                                        })
                                                    } else {
                                                        console.log(custid, date, "no posts");
                                                        dcb();
                                                    }
                                                })


                                            })

                                        } else {
                                            console.log(custid, date, "no posts");
                                            dcb();
                                        }
                                    })

                                }, function () {
                                    console.log(doc.custid);
                                    way2_uninstall_data.collection(data_collection).updateMany({custid: custid}, {$set:{processed:1}}, function (err, ok) {
                                        cb();
                                    })

                                })
                            }, function () {
                                console.log("completed");
                                setTimeout(getData,0);
                            })

                        }else {
                            console.log("errrr",err)
                        }
                    })
                }
                getData()
            }
        });


    }
});