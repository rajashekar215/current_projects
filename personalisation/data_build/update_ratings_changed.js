
const async = require("async");
const mongo = require('mongodb');
const MongoClient = require('mongodb').MongoClient;
const config = require('./config/properties_r')
const poolsel = require('./dbconnection/dbsel');
const groupBy = require("group-by");
const dateTime = require('node-datetime');
var moment = require("moment")

let emails = [
  // "raju@way2online.net"

  "mahesh.m@way2online.co.in",
  "sandeep.kumar@way2online.co.in",
  "samara.k@way2online.co.in",
  "lokesh.n@way2online.co.in",
  "kartikeya.r@way2online.co.in",
  "jilani.m@way2online.co.in",
  "rinkisanyal8@gmail.com",
  "shaikkhaja.n@way2online.co.in",
  "akhilesh.c@way2online.co.in",
  "rahul.m@way2online.co.in",
  "rajesh.nadimpalli@way2online.co.in",
  "anilkumar.m@way2online.co.in",
  "varsha.b@way2online.co.in",
  "divyasree.d@way2online.co.in",
  "vishal.b@way2online.co.in",
  "ravi.kiran@way2online.co.in",
  "kritika.g@way2online.co.in",
  "kalyani.s@way2online.co.in",
  "nirmala.t@way2online.co.in",
  "gowthami.g@way2online.co.in",
  "rajesh.dattla@way2online.co.in",
  "ramaraju.m@way2online.co.in",
  "ramakrishnam.r@way2online.co.in",
  "sivakoteswararao.a@way2online.co.in",
  "kshitij.k@way2online.co.in",
  "dinesh.k@way2online.co.in",
  "vikrant.d@way2online.co.in",
  "sharat@way2online.com",
  "krishna.c@way2online.co.in",
  "sharmishtha.k@way2online.co.in",
  "sameer.b@way2online.co.in",
  "nagaraju.d@way2online.co.in",
  "vinodkumar.k@way2online.co.in",
  "misbah.s@way2online.co.in",
  "likhita.b@way2online.co.in",
  "satyasri.k@way2online.co.in",
  "abhinav.d@way2online.co.in",
  "krishna.varshney@way2online.co.in",
  "laxman.g@way2online.co.in",
  "vivekrao.v@way2online.co.in",
  "krishnakishore.v@way2online.co.in",
  "nikhil.b@way2online.co.in",
  "pratibha.s@way2online.co.in",
  "sowjanya.b@way2online.com",
  "lathif.s@way2online.co.in",
  "bhavani.b@way2online.co.in",
  "yoosaf.k.v@way2online.co.in",
  "dharmateja.m@way2online.co.in",
  "srinivasachary.r@way2online.co.in",
  "towfiq.ali@way2online.com",
  "bitu.g@way2online.co.in",
  "rainak.d@way2online.co.in",
  "vijil.ac@way2online.co.in",
  "venkateswarareddy.k@way2online.co.in",
  "shantanu.c@way2online.co.in",
  "anilchandra.g@way2online.co.in",
  "manojkumar.g@way2online.co.in",
  "sreejani.b@way2online.co.in",
  "anilkumar.r@way2online.co.in",
  "goutham.b@way2online.com",
  "rucillidevi.l@way2online.co.in",
  "arshad.k@way2Online.net",
  "arpit.sharma@way2online.net",
  "misha.b@way2online.net",
  "rohit.kumar@way2online.net",
  "surendra.varma@way2online.co.in",
  "triveni.c@way2online.co.in",
  "priya.p@way2online.co.in",
  "prasanna.v@way2online.co.in",
  "shant.p@way2online.co.in",
  "saireddy.t@way2online.co.in",
  "avinash.chittiboyana@way2online.co.in",
  "deepika.g@way2online.co.in",
  "manoj@way2online.com",
  "mallikarjunarao.g@way2online.co.in",
  "tejavijayramaraju.d@way2online.co.in",
  "suman@way2online.com",
  "sravan.t@way2online.co.in",
  "saiamith@way2online.co.in",
  "Hemanth.ch@way2online.co.in",
  "gopiprasad.d@way2online.co.in",
  "pradeep.p@way2online.co.in",
  "muralikrishna.g@way2online.co.in",
  "devaswin@way2online.net",
  "raju@way2online.net",
  "pavankumar1528@gmail.com",
  "rangarao.d@way2online.co.in",
  "murshad.c@way2online.co.in",
  "kollururamana453@gmail.com",
  "karthik.r@way2online.net",
  "vigneshgk4@gmail.com",
  "padmapriya434@gmail.com",
  "journalistdeepak1@gmail.com",
  "kamakerinaveen56@gmail.com",
  "joiedevivre.simon@gmail.com",
  "flame.god7@gmail.com",
  "prashanthku15@gmail.com",
  "anu.deepu08@gmail.com",
  "venkiraj54@gmail.com",
  "revanth.t@way2online.co.in",
  "rajeshkomakula11@gmail.com",
  "kailash.ecm@gmail.com",
  "pvk047@gmail.com",
  "anilkumar.m@way2online.co.in",
  "punna574@gmail.com",
  "jindamchandrakanth@gmail.com",
  "tharsha1987@gmail.com",
  "maheshmaroju@gmail.com",
  "harika.uppula@gmail.com",
  "gani7129@gmail.com",
  "swamy.reddy1234@gmail.com",
  "leosreejani@gmail.com",
  "nadimpallirajeshraju@gmail.com",
  "Priyanka.guth@gmail.com",
  "bheema.ratna@gmail.com",
  "Sampath.lepakshi@gmail.com",
  "Prathipatimanojchowdary@gmail.com",
  "aanilkumar2321@gmail.com",
  "m.yasaswini94@gmail.com",
  "Sunkara0007@gmail.com",
  "a.girishkumar3222@gmail.com",
  "Vamshi0712@gmail.com",
  "tejapericherla@gmail.com",
  "ashokn369@gmail.com",
  "Anil.chandra1@gmail.com",
  "Sukeshcjr@gmail.com",
  "dinu114@gmail.com",
  "krishr10@gmail.com",
  "kammaribabu24@gmail.com",
  "gade.praven@gmail.com",
  "ganesh.gummalla@gmail.com",
  "damarla.raja@gmail.com",
  "chegireddy07@gmail.com"
];

let custidsArr = [];
// let datesArr = ["2019-08-01","2019-08-02","2019-08-03","2019-08-04","2019-08-05","2019-08-06","2019-08-07","2019-08-08","2019-08-09","2019-08-10","2019-08-11","2019-08-12"];
let datesArr = ["2019-08-13"];

console.time();
// start();


// start function 
// function start() {
//     let custidsArr = [];

//     //for getting custids from emails
//     async.forEach(emails, function (email, emailCb) {
//         let custIdQry = "SELECT t1.Email,t1.custid, t2.lang_id from user_register t1 join user_preferences t2 on t1.custid = t2.custid where t1.Email = ? Order By t1.regDate DESC limit 1 ";
//         let params = [];
//         params.push(email);

//         executeAndCB('select', custIdQry, params, function (err, res) {
//             console.log(res);
//             if (!err) {
//                 if (res.length != 0) {

//                     custidsArr.push({ custid: res[0].custid, email: res[0].Email });
//                     emailCb();
//                 } else {
//                     console.log(email + " not found");
//                     emailCb();
//                 }
//             } else {
//                 console.log(err);
//             }
//         })
//     }, function (success) {
//         console.log(custidsArr)
//         // //for building custids giving custids to buildData function 
//         // console.log("for all emails custids built", custidsArr);
//         // buildData(custidsArr, datesArr, function (Cb) {
//         //     if (Cb) {
//         //         console.log("Successfully done");
//         //         console.timeEnd();
//         //     }
//         // })
//     })
// }
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
let default_avg_time_spent=8;
function get_custid_ratings() {
  MongoClient.connect(config.localMongodb.uri, function (err, localdb) {
    if (localdb != null) {
      localdb.collection(config.localMongodb.testing_users).find({
        // custid:22172222,
        rating: { $in: [0, null] } 
      }).toArray(function (err, docs) {
        if (!err && docs) {
          // console.log(docs)
          if (docs.length > 0) {
            console.log("testing custids fetched from mongo:: ", docs.length)
            MongoClient.connect(config.liveMongodb.uri, function (err, livedb) {
              if (livedb != null) {
                async.eachSeries(docs, function (doc, asyncCb) {
                  let custid = doc.custid;
                  let langid = doc.langid;
                  let avg_time_spent = doc.avg_time_spent ? doc.avg_time_spent : default_avg_time_spent;
    
                  console.log("upating for custid:: ", custid, doc)
                  console.log("avg spent time:: ",avg_time_spent)
    
                  let today_date = dateTime.create().format('Y-m-d H:M:S').split(" ")[0]
                  // let today_date = "2019-09-16"
                  let last_post_date = doc.last_post_date ? doc.last_post_date : today_date
                  let last_post_time = doc.last_post_time ? doc.last_post_time : "0"
                  let datesArr = []
                  console.log(last_post_date)
                  if (today_date != last_post_date) {
                    datesArr = getDates(last_post_date, today_date, last_post_time)
                  } else {
                    datesArr.push({ date: last_post_date, time: last_post_time })
                  }
                  console.log(datesArr)
                  if(datesArr.length>0){
                   
                  getFlippedPosts(livedb,localdb, custid, langid, datesArr, avg_time_spent, function (rtdata) {
                    if (rtdata) {

                      localdb.collection(config.localMongodb.testing_users).updateOne({ custid: custid }, { $set: { rating: 1, last_post_date: rtdata.new_last_post_date ? rtdata.new_last_post_date : today_date, last_post_time: rtdata.new_last_post_time ? rtdata.new_last_post_time : "0" } }, { upsert: true }, function (err, success) {
                          if (!err) {
                              console.log("ratings for custid " + custid)
                          } else {
                              console.log(err);
                          }
                          console.log("for one user data is built");
                          asyncCb();
                      })
                      // asyncCb();
    
                    }
                  })
               
                }
    
                }, function (success) {
                  console.log("****************all custids ratings updated****************************")
                  console.log("all connections: ", poolsel._allConnections.length)
                  console.log("free connections: ", poolsel._freeConnections.length)
                  localdb.close();
                  livedb.close();
                  poolsel.end()
                  // setTimeout(get_custid_ratings, 0);
                })
              }
            });
            
          } else {
            console.log("no testing custids found")
            localdb.collection(config.localMongodb.testing_users).updateMany({}, { $set: { rating:0} }, { upsert: true }, function (err, success) {
                // db.close();
                if (!err) {
                    console.log("all custids updated")
                    setTimeout(get_custid_ratings, 0);
                } else {
                    console.log(err);
                }
            })
          }
        } else {
          console.log(err);
        }
      })
    } else {
      console.log(err)
    }
  });
}

//inserting custids in active_users collection and calling getFlippedPosts function 
// function buildData(custidsArr, datesArr, Cb) {
//     async.eachSeries(custidsArr, function (custid, asyncCb) {
//         try {
//             //for inserting custids in separate collection active_users
//             MongoClient.connect(config.localMongodb.uri, function (err, db) {

//                 if (db != null) {
//                     db.collection(config.localMongodb.activesCollection).updateOne({ _id: custid }, { status: 0 }, { upsert: true }, function (err, success) {
//                         db.close();
//                         if (!err) {
//                             console.log("custid inserted mongo ")
//                         } else {
//                             console.log(err);
//                         }
//                     })
//                 } else {
//                     console.log(err)
//                 }
//             });
//         } catch (err) {
//             console.log(err);
//         }
//         //for building data
//         getFlippedPosts(custid, datesArr, function (Cb) {
//             if (Cb) {

//                 console.log("for one user data is built");
//                 asyncCb();
//             }
//         })
//     }, function (success) {
//         Cb(true);
//     })
// }

function getFlippedPosts(livedb,localdb, custid, langid, datesArr, avg_time_spent, userCb) {
  let new_last_post_date = ""
  let new_last_post_time = ""
  async.forEachOf(datesArr, (dateobj,dateindex, asyncCb) => {
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
      datestring += " 00:00:00"
    }

    console.log("date ::::::::::::::::::", date)
    console.log("all connections: ", poolsel._allConnections.length)
    console.log("free connections: ", poolsel._freeConnections.length)
    let month = new Date(date).getMonth() + 1;
    let year = new Date(date).getFullYear();
    let day = new Date(date).getDate();

    try {
      //for fetching flips posts data of user
      // MongoClient.connect(config.liveMongodb.uri, function (err, db) {

      //   if (db != null) {
          console.log(datestring, "  objectid:: ", mongo.ObjectID(objectIdFromDate(new Date(datestring))))
          livedb.collection("track_posts_cat_" + day + "_" + month + "_" + year).find({
            _id: { $gt: mongo.ObjectID(objectIdFromDate(new Date(datestring))) },
            custid: custid,
            cat_id: { $ne: 2 },
            // time1: { $gt: time }
          }, {}, {
              sort: {
                // seen_time: 1
                _id: 1
              }
            }).toArray(function (err, result) {
              // db.close();

              if (!err) {
                // console.log("posts length " + JSON.stringify(result));
                if (result && result.length > 0) {
                  getfirstConn((conn) => {
                    let mysqlConn = conn;


                    function getConn(Cb) {

                      try {
                        poolsel.getConnection(function (err, con1) {
                    
                          if (err) {
                            console.error('error while fetching conn ', err);
                            process.exit(0);
                    
                          } else if (con1) {
                            console.log("new mysql connection established*****************************")
                            Cb(con1);
                          } else {
                            console.error('No connection found.')
                            process.exit(0);
                          }
                        });
                    
                      } catch (cerr) {
                        console.error('unkown error occured in getCOnn');
                        console.error(cerr);
                        process.exit(0);
                      }
                    
                    }
                    
                    function releaseConn() {
                      if (mysqlConn) {
                        mysqlConn.release();
                        mysqlConn = null;
                        console.log("Mysql Connection released***********************************");
                      }
                    }
                    
                    //this function is used to execute all mysql queries
                    function executeAndCB(type, query, data, eacb) {
                      if (mysqlConn) {
                        if (type === 'select') {
                    
                          try {
                            if (mysqlConn) {
                              mysqlConn.query(query, data, function (err, response) {
                                // con1.release();
                    
                                eacb(err, response);
                              });
                            } else {
                              console.log('invalid connection');
                              process.exit(0)
                            }
                          } catch (cerr) {
                            console.error('unkown error occured in executeAndCB');
                            console.error(cerr);
                            eacb('unkown error occured in executeAndCB');
                          }
                        } else {
                          console.log("operation not allowed");
                        }
                      } else {
                        console.log("########### COnnection Not Found ###############");
                        getConn((conn) => {
                          mysqlConn = conn;
                          executeAndCB(type, query, data, function (err, response) {
                            eacb(err, response);
                          });
                        })
                      }
                    }



                    let pushPosts = [];
                    if (langid) {
                      let pushPostsQry = "SELECT post_id FROM push_notifications_queue WHERE lang_id=1 AND  push_date= ?";
                      let pushPostPrms = [langid, date];

                      executeAndCB('select', pushPostsQry, pushPostPrms, function (perr, res) {
                        if (!err) {
                          pushPosts = res;
                        } else {
                          console.error(perr);
                          process.exit(0);
                        }
                        async.forEachOf(result, function (item, index, itemCb) {
                          let finalPOstObj = {}

                          async.waterfall([
                            //for time spent on post
                            (done) => {

                              if (index == (result.length - 1)) {
                                if(dateindex==(datesArr.length-1)){
                                  new_last_post_date = item.date1
                                  new_last_post_time = item.time1
                                }
                                
                                finalPOstObj["post_id"] = item.postid;
                                finalPOstObj["seen_time"] = item.time1;
                                finalPOstObj["time_spent"] = "-";
                                done(null)
                              } else {
                                let time1 = item.time1;
                                let time2 = result[index + 1].time1;
                                // console.log("time1 :: ", time1);
                                // console.log("time2 :: ", time2, index);
                                time1 = time1.split(":");
                                time2 = time2.split(":");
                                let date1 = new Date(year, month, day, time1[0], time1[1], time1[2]);
                                let date2 = new Date(year, month, day, time2[0], time2[1], time2[2]);
                                let timeInSeconds = Math.abs(date2.getTime() - date1.getTime()) / 1000;
                                let minutes = Math.floor(timeInSeconds / 60);
                                let seconds = timeInSeconds % 60;
                                // console.log(timeInSeconds)
                                // console.log(minutes * 60 + seconds)
                                finalPOstObj["post_id"] = item.postid;
                                finalPOstObj["seen_time"] = item.time1;
                                finalPOstObj["time_spent"] = minutes * 60 + seconds;
                                done(null)
                              }
                            }, (done) => {

                              async.parallel({
                                getTags: (kwCb) => {
                                  let tagQry = "SELECT lower(tag_name) as tag_name FROM way2app.mag_posts_home_tags_relation as t1 join way2app.mag_tags_home as t2 on t1.tag_id = t2.tag_id where post_id = ? ";
                                  let tagPrms = [];

                                  tagPrms.push(item.postid);

                                  executeAndCB('select', tagQry, tagPrms, (err, tagRes) => {

                                    if (!err) {
                                      let tags = [];
                                      async.eachOfSeries(tagRes, (tagPrms, index, CB) => {
                                        let keyword = tagRes[index].tag_name;
                                        keyword = keyword.replace(/\./g, ' ');
                                        tags.push(keyword);
                                        CB();
                                      }, function (sucess) {
                                        kwCb(null, tags);
                                      })
                                    } else {
                                      console.log("tagQry Query ", tagQry);
                                      console.log("all connections: ", poolsel._allConnections.length)
                                      console.log("free connections: ", poolsel._freeConnections.length)
                                      console.log("Some error occured while fetching details", err);
                                    }
                                  });


                                },
                                getCategory: (CtgryCb) => {
                                  let ctgryQry = "SELECT category_name,post_desc,post_title FROM way2app.mag_posts_home_new where post_id = ? limit 1";
                                  let ctgeryPrms = [];
                                  ctgeryPrms.push(item.postid);
                                  executeAndCB('select', ctgryQry, ctgeryPrms, (err, ctgryRes) => {
                                    // console.log(err + " category response" + JSON.stringify(ctgryRes) + " " + item.postid);
                                    if (!err) {
                                      if (ctgryRes != '' && ctgryRes != undefined && ctgryRes.length > 0) {
                                        CtgryCb(null, { cat_name: ctgryRes[0].category_name, post_desc: ctgryRes[0].post_desc, post_title: ctgryRes[0].post_title });
                                      } else {
                                        CtgryCb(null, '');
                                      }
                                    } else {
                                      console.log("Query ", ctgryQry);
                                      console.log("Some error occured while fetching category name ", err);
                                      console.log("all connections: ", poolsel._allConnections.length)
                                      console.log("free connections: ", poolsel._freeConnections.length)
                                    }
                                  })
                                },
                                getRating: (rtngCb) => {
                                  // random rating between 0 to 5
                                  // min = 0;
                                  // max = 5;
                                  // let rating = Math.floor(Math.random() * (max - min + 1)) + min;

                                  async.waterfall([
                                    (done) => {
                                      if (pushPosts && pushPosts.length > 0 && pushPosts.include(item.postid)) {

                                        let pushSharetable = "push_share_opens_" + month + "_" + year;
                                        let query = "SELECT count(*) as count FROM " + pushSharetable + " where custid = ? and post_id = ? and from_unixtime(clicked_date,'%Y-%m-%d') = ?";
                                        let params = [];
                                        params.push(custid);
                                        params.push(item.postid);

                                        params.push(date);
                                        // console.log("******************************************************");

                                        try {
                                          executeAndCB('select', query, params, function (err, sqlResponse) {
                                            // console.log(" push share opens db response " + date + " " + JSON.stringify(sqlResponse))


                                            if (sqlResponse && sqlResponse.length > 0) {
                                              // console.log("first done");
                                              finalPOstObj["isPushOpen"] = sqlResponse[0].count;
                                              done(null)
                                            } else {
                                              finalPOstObj["isPushOpen"] = sqlResponse.length;
                                              done(null);
                                            }

                                          });
                                        } catch (error) {
                                          // console.log
                                          console.log(error);
                                          done(null);
                                        }
                                      } else {
                                        done(null);
                                      }
                                    }, (done) => {
                                      try {

                                        // if (db != null) {
                                          livedb.collection("posts_events_tracking_" + month + "_" + year).find({

                                            post_id: item.postid,
                                            track_date: date,
                                            cust_id: custid

                                          }).toArray(function (err, result) {
                                            // console.log(" events db response " + date + " " + JSON.stringify(result))

                                            // db.close();
                                            if (!err) {

                                              if ((result != undefined || result != null) && result.length > 0) {
                                                let obj = {};
                                                // console.log("events ::::::: ",result);
                                                async.forEach(result, function (event, eventCb) {
                                                  obj[event.con_type] = 1;
                                                  eventCb();
                                                }, function (suc) {
                                                  // console.log("second done");
                                                  finalPOstObj["events"] = obj;
                                                  done(null)
                                                });
                                              } else {
                                                // console.log("second done no data");
                                                done(null);
                                                finalPOstObj["events"] = {};
                                              }
                                            } else {
                                              done(null)
                                            }
                                          })

                                        // } else {
                                        //   done(null)
                                        // }


                                      } catch (e) {

                                        console.log(e);
                                        done(null);
                                      }

                                    }, (done) => {

                                      // console.log("third done");
                                      // console.log("result Obj for Calculate rating is ::::: " + JSON.stringify(finalPOstObj));
                                      let points = 0;
                                      // if (finalPOstObj["events"] && finalPOstObj["events"].videoclick) {
                                      //     points += config.ratingPoints.video_click;
                                      // }
                                      if (finalPOstObj["events"] && finalPOstObj["events"].video_play_time >= config.ratingPoints.video_play_time) {
                                        // points += config.ratingPoints.video_play_time_points;
                                        points += 1
                                      } else if (finalPOstObj.time_spent && finalPOstObj.time_spent != "-" && finalPOstObj.time_spent >= avg_time_spent ) {
                                        // points += config.ratingPoints.post_spent_time_points;
                                        points += 1
                                      }

                                      if (finalPOstObj["events"] && (finalPOstObj["events"].addbookmark || finalPOstObj["events"].full_img_ad_click || finalPOstObj["events"].titleclick || finalPOstObj["events"].screenshots || finalPOstObj["events"].picdownload)) {
                                        // points += config.ratingPoints.bookmark;
                                        points += 2
                                      }

                                      if (finalPOstObj["events"] && (finalPOstObj["events"].comments || finalPOstObj["events"].likeclick_one)) {
                                        // points += config.ratingPoints.comments;
                                        points += 3
                                      }

                                      if ((finalPOstObj["isPushOpen"]) || (finalPOstObj["events"] && (finalPOstObj["events"].facebookshare || finalPOstObj["events"].whatsappshare || finalPOstObj["events"].twittershare || finalPOstObj["events"].othershare))) {
                                        // points += config.ratingPoints.shares;
                                        points += 4
                                      }

                                      // if (finalPOstObj["events"] && finalPOstObj["events"].notification_clear) {
                                      //     points += config.ratingPoints.notification_clear;
                                      // }
                                      rtngCb(null, points);
                                    }
                                  ]);
                                }
                              }, function (err, result) {
                                if ((finalPOstObj["events"] && Object.keys(finalPOstObj["events"]).length > 0) || (finalPOstObj.time_spent && finalPOstObj.time_spent != "-" && finalPOstObj["time_spent"] < 100)) {
                                   if (finalPOstObj.time_spent && finalPOstObj.time_spent == "-") {
                                    finalPOstObj["time_spent"]=100
                                   }
                                  // console.log("for one post data is built ");

                                  //this is final obj we are inserting
                                  let finalUserObj = {};
                                  finalUserObj["custid"] = custid;
                                  finalUserObj["date"] = date;
                                  finalUserObj["postid"] = item.postid;
                                  finalUserObj["seen_time"] = item.time1;
                                  finalUserObj["seen_unix_time"] = new Date(date + " " + item.time1).getTime();
                                  finalUserObj["keywords"] = result.getTags;
                                  if(finalPOstObj["events"] && Object.keys(finalPOstObj["events"]).length > 0){
                                    finalUserObj["events"] = 1;
                                  }
                                  if (result.getCategory != '') {
                                    finalUserObj["category"] = result.getCategory.cat_name;
                                    finalUserObj["post_desc"] = result.getCategory.post_desc;
                                    finalUserObj["post_title"] = result.getCategory.post_title;

                                  }
                                  // delete finalPOstObj.post_id
                                  // delete finalPOstObj.seen_time
                                  // finalUserObj["reaction"] = finalPOstObj
                                  // let rtng = result.getRating;
                                  // let incrtng = result.getRating;

                                  // console.log("finalUser Obj " + JSON.stringify(finalUserObj));



                                  // MongoClient.connect(config.localMongodb.uri, (err, db) => {
                                  //   if (db != null) {
                                      localdb.collection(config.localMongodb.ratingCollection).findOne({ custid: custid, postid: item.postid }, {}, function (err, Doc) {
                                        let final_rating = 0;
                                         
                                        if (Doc) {
                                          final_rating = Doc.rating > result.getRating ? Doc.rating : result.getRating;
                                          finalUserObj["max_time_spent"] = Doc["max_time_spent"] > finalPOstObj["time_spent"] ? Doc["max_time_spent"] : finalPOstObj["time_spent"]
                                        } else {
                                          // console.log("no previous doc");
                                          final_rating = result.getRating;
                                            finalUserObj["max_time_spent"] = finalPOstObj["time_spent"]
                                        }
                                        finalUserObj["rating"] = final_rating;

                                        localdb.collection(config.localMongodb.ratingCollection).updateOne({ custid: custid, postid: item.postid }, { $set: finalUserObj, $push: { reaction: finalPOstObj } }, { upsert: true }, function (err, res) {
                                          if (err) throw err;
                                          // console.log("One Post Data is inserted in mongo");
                                          let keywords = finalUserObj["keywords"];
                                          let category = finalUserObj["category"]
                                          // async.eachOfSeries(keywords,(keyword,index,asyCb)=>{
                                          localdb.collection(config.localMongodb.userKeywordsCollection).findOne({ custid: custid }, {}, (err, docs) => {

                                            if (!err) {

                                              if (docs) {
                                                // if (keywords.indexOf("radhasapthami") > -1) {
                                                //     rad++;
                                                //     console.log(keywords, "--------->", result.getRating, final_rating)
                                                // }
                                                async.forEach(keywords, (keyword, CB) => {
                                                  keyword = keyword.replace(/\./g, ' ');
                                                  if (docs[keyword]) {
                                                    docs[keyword] += result.getRating;
                                                  } else {
                                                    docs[keyword] = result.getRating;
                                                  }
                                                  if (docs["category"] && docs["category"][category]) {
                                                    docs["category"][category] += result.getRating;
                                                  } else {
                                                    if (docs["category"]) {
                                                      docs["category"][category] = result.getRating
                                                    } else {
                                                      docs["category"] = {}
                                                      docs["category"][category] = result.getRating
                                                    }
                                                  }
                                                  CB();
                                                }, function (success) {
                                                  localdb.collection(config.localMongodb.userKeywordsCollection).updateOne({ custid: custid }, { $set: docs }, (err, success) => {
                                                    if (!err) {
                                                      // console.log("succesfully updated");
                                                      // console.log("******************************************************");
                                                      // db.close();
                                                      itemCb();
                                                    } else {
                                                      console.log(err);
                                                      // db.close();
                                                      itemCb();
                                                    }
                                                  })
                                                })

                                              } else {
                                                let docs = {};
                                                docs["custid"] = custid;

                                                async.forEach(keywords, (keyword, CB) => {
                                                  keyword = keyword.replace(/\./g, ' ');

                                                  docs[keyword] = result.getRating;
                                                  docs["category"] = {}
                                                  docs["category"][category] = result.getRating
                                                  CB();
                                                }, function (success) {

                                                  localdb.collection(config.localMongodb.userKeywordsCollection).updateOne({ custid: custid }, { $set: docs }, { upsert: true }, (err, success) => {
                                                    // console.log(err + " " + success)
                                                    if (!err) {
                                                      // console.log("succesfully updated");
                                                      // console.log("******************************************************");
                                                      // db.close();
                                                      itemCb();
                                                    } else {
                                                      console.log(err);
                                                      // db.close();
                                                      itemCb();
                                                    }
                                                  })
                                                })
                                              }
                                              // if(rad==3)process.exit(0);

                                            } else {
                                              console.log("some error occured ", err);
                                            }
                                          })

                                        });
                                      });
                                  //   } else {
                                  //     console.log("Error while connecting local mongo db :: ", err);
                                  //   }
                                  // });

                                } else {
                                  // console.log("NO event or time spent greater than 100s");
                                  itemCb();
                                }
                              });
                            }
                          ])



                        }, function (done) {
                          let edt = Date.now();
                          console.log(`On ${date} all posts data built`);
                          console.log(`${result.length} posts   time taken:  ${(edt - dst) / 1000}`);
                          console.log("all connections: ", poolsel._allConnections.length)
                          console.log("free connections: ", poolsel._freeConnections.length)
                          releaseConn();
                          asyncCb();
                        });

                      })

                    }else{
                      releaseConn();
                      asyncCb();
                    }
                  })
                  //for iterating each post on that day and insert stats in db
                  // async.forEachOf


                } else if (result && result.length == 0) {
                  if(dateindex==(datesArr.length-1)){
                  new_last_post_date = date
                  new_last_post_time = "0"
                  }
                  let edt = Date.now();
                  console.log(`User didn't see the posts on ${date}`);
                  console.log(`${result.length} posts   time taken:  ${(edt - dst) / 1000}`);
                  // console.log("all connections: ", poolsel._allConnections.length)
                  // console.log("free connections: ", poolsel._freeConnections.length)
                  // releaseConn();
                  asyncCb();
                }



              } else {
                console.log("Error while getting Data  :: ", err);
              }
            })
      //   } else {
      //     console.log("Error while connecting live mongo db :: ", err);
      //   }
      // })
    } catch (e) {
      console.log("Exception while building Data :: ", e);
    }
  }, function (success) {
    console.log("one user data stored in db for given dates");
    // releaseConn();
    userCb({ new_last_post_date: new_last_post_date, new_last_post_time: new_last_post_time });
  });


}
function getfirstConn(Cb) {

  try {
    poolsel.getConnection(function (err, con1) {

      if (err) {
        console.error('error while fetching conn ', err);
        process.exit(0);

      } else if (con1) {
        console.log("new mysql connection established*****************************")
        Cb(con1);
      } else {
        console.error('No connection found.')
        process.exit(0);
      }
    });

  } catch (cerr) {
    console.error('unkown error occured in getCOnn');
    console.error(cerr);
    process.exit(0);
  }

}

// function releaseConn() {
//   if (mysqlConn) {
//     mysqlConn.release();
//     mysqlConn = null;
//     console.log("Mysql Connection released***********************************");
//   }
// }

// //this function is used to execute all mysql queries
// function executeAndCB(type, query, data, eacb) {
//   if (mysqlConn) {
//     if (type === 'select') {

//       try {
//         if (mysqlConn) {
//           mysqlConn.query(query, data, function (err, response) {
//             // con1.release();

//             eacb(err, response);
//           });
//         } else {
//           console.log('invalid connection');
//           process.exit(0)
//         }
//       } catch (cerr) {
//         console.error('unkown error occured in executeAndCB');
//         console.error(cerr);
//         eacb('unkown error occured in executeAndCB');
//       }
//     } else {
//       console.log("operation not allowed");
//     }
//   } else {
//     console.log("########### COnnection Not Found ###############");
//     getConn((conn) => {
//       mysqlConn = conn;
//       executeAndCB(type, query, data, function (err, response) {
//         eacb(err, response);
//       });
//     })
//   }
// }

// function executeAndCB2(type, query, data, cb) {
//   // let sqlConnection = null;
//   if (type === 'select') {
//     getConn((connection) => {
//       if (connection) {
//         connection.query(query, data, (err, response) => {
//           connection.release();
//           cb(err, response);
//         });
//       } else {
//         console.log('No connection found from get conn function.')
//         cb(new Error("No connection found"), null)
//       }
//     })
//   } else {
//     console.log('Operation not allowed.')
//     cb(null, null)
//   }
// }


get_custid_ratings()

