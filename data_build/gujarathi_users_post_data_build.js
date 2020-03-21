
const async = require("async");
const mongo = require('mongodb');
const MongoClient = require('mongodb').MongoClient;
const config = require('./config/properties_gujarathi')
const poolsel = require('./dbconnection/dbsel');
const dateTime = require('node-datetime');
var moment = require("moment")


let custidsArr = [];
// let datesArr = ["2019-08-01","2019-08-02","2019-08-03","2019-08-04","2019-08-05","2019-08-06","2019-08-07","2019-08-08","2019-08-09","2019-08-10","2019-08-11","2019-08-12"];
let datesArr = ["2019-08-13"];

console.time();

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

function reset(localdb, lcb) {

  // Get the collection and bulk api artefacts
  let col = localdb.collection(config.localMongodb.testing_users),
    bulk = col.initializeUnorderedBulkOp() // Initialize the Ordered Batch
  // ,counter = 0;

  // Case 1. Change type of value of property, without changing the value. 
  col.find({ "rating": 1 }).limit(1000).toArray(function (err, docs) {
    if (docs && docs.length > 0) {
      async.forEach(docs, function (doc, cb) {
        bulk.find({ "_id": doc._id }).updateOne({
          "$set": { "rating": 0 }
        });
        cb()
      }, function () {
        bulk.execute(function (err, result) {
          setTimeout(function(){
            reset(localdb,function(){
              lcb()
            })
          }, 0)
        });
      })
    } else {
      lcb()
    }
  })
}

let default_avg_time_spent = 8;
function get_custid_ratings() {
  MongoClient.connect(config.localMongodb.uri, function (err, localdb) {
    if (localdb != null) {
      localdb.collection(config.localMongodb.testing_users).find({
        // custid:198033,
        rating: { $in: [0, null] }
      }).limit(10).toArray(function (err, docs) {
        if (!err && docs) {
          // console.log(docs)
          if (docs.length > 0) {
            console.log("testing custids fetched from mongo:: ", docs.length)
            MongoClient.connect(config.liveMongodb.uri, function (err, livedb) {
              if (livedb != null) {
                console.log("live db connected")
                async.forEach(docs, function (doc, asyncCb) {
                  let custid = doc.custid;
                  let langid = doc.lang_id;
                  let avg_time_spent = doc.avg_time_spent ? doc.avg_time_spent : default_avg_time_spent;
                  let total_posts = doc.total_posts ? doc.total_posts : 0;
                  console.log("upating for custid:: ", custid)
                  console.log("avg spent time:: ", avg_time_spent)

                  let today_date = dateTime.create().format('Y-m-d H:M:S').split(" ")[0]
                 //let today_date = "2020-01-06"
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
                  if (datesArr.length > 0) {

                    getFlippedPosts(livedb, localdb, custid, langid, datesArr, avg_time_spent, function (rtdata) {
                      if (rtdata) {
                        let set_doc = { rating: 1, last_post_date: rtdata.new_last_post_date ? rtdata.new_last_post_date : today_date, last_post_time: rtdata.new_last_post_time ? rtdata.new_last_post_time : "0" }
                        let updated_total_posts = rtdata.new_total_posts + total_posts
                        let new_avg_time_spent = (avg_time_spent * total_posts + rtdata.time_spent_sum) / updated_total_posts
                        if (new_avg_time_spent >= default_avg_time_spent && new_avg_time_spent < 15) {
                          set_doc["avg_time_spent"] = new_avg_time_spent
                        }
                        set_doc["total_posts"] = updated_total_posts
                        //   console.log(set_doc)
                        localdb.collection(config.localMongodb.testing_users).updateMany({ custid: custid }, { $set: set_doc }, { upsert: true }, function (err, success) {
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
                  // poolsel.end()
                  setTimeout(get_custid_ratings, 0);
                })
              } else {
                console.log("live db not connecting")
              }
            });

          } else {
            console.log("no testing custids found")
            reset(localdb, function () {
              localdb.close()
              console.log("all custids updated")
               setTimeout(get_custid_ratings,5*60*60)
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


function getFlippedPosts(livedb, localdb, custid, langid, datesArr, avg_time_spent, userCb) {
  let new_last_post_date = ""
  let new_last_post_time = ""
  let time_spent_sum = 0
  let new_total_posts = 0
  async.forEachOf(datesArr, (dateobj, dateindex, asyncCb) => {
    let dst = Date.now();
    let date = dateobj.date;
    let time = dateobj.time;
    let datestring = date;
    if (time != "0") {
      let new_time = time.split(":")
      if (parseInt(new_time[2]) + 1 < 60) {
        new_time[2] = parseInt(new_time[2]) + 1
      } else if (parseInt(new_time[1]) + 1 < 60) {
        new_time[1] = parseInt(new_time[1]) + 1
        new_time[2] = "00"
      } else {
        new_time[0] = parseInt(new_time[0]) + 1
        new_time[1] = "00"
        new_time[2] = "00"
      }
      new_time = new_time.join(":")
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
      // console.log(datestring, "  objectid:: ", mongo.ObjectID(objectIdFromDate(new Date(datestring))))
      console.log("track_posts_cat_" + day + "_" + month + "_" + year)
      console.log(datestring)
      console.log(mongo.ObjectID(objectIdFromDate(new Date(datestring))))
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
          console.log("posts length " + result.length);
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

              if (langid) {

                async.forEachOf(result, function (item, index, itemCb) {
                  let finalPOstObj = {}

                  async.waterfall([
                    //for time spent on post
                    (done) => {

                      if (index == (result.length - 1)) {
                        if (dateindex == (datesArr.length - 1)) {
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
                        getCategory: (CtgryCb) => {
                          let ctgryQry = "SELECT category_name,post_desc,post_title,lang_id FROM way2app.mag_posts_home_new where post_id = ? limit 1";
                          let ctgeryPrms = [];
                          ctgeryPrms.push(item.postid);
                          executeAndCB('select', ctgryQry, ctgeryPrms, (err, ctgryRes) => {
                            // console.log(err + " category response" + JSON.stringify(ctgryRes) + " " + item.postid);
                            if (!err) {
                              if (ctgryRes != '' && ctgryRes != undefined && ctgryRes.length > 0) {
                                CtgryCb(null, { cat_name: ctgryRes[0].category_name, post_desc: ctgryRes[0].post_desc, post_title: ctgryRes[0].post_title, langid: ctgryRes[0].lang_id });
                              } else {
                                CtgryCb(null, '');
                              }
                            } else {
                              // console.log("Query ", ctgryQry);
                              console.log("Some error occured while fetching category name ", err);
                              console.log("all connections: ", poolsel._allConnections.length)
                              console.log("free connections: ", poolsel._freeConnections.length)
                            }
                          })
                        },
                      }, function (err, result) {
                        if (finalPOstObj.time_spent && finalPOstObj.time_spent != "-" && finalPOstObj.time_spent >= avg_time_spent) {
                          if (finalPOstObj.time_spent < 60) {
                            new_total_posts++
                            time_spent_sum += finalPOstObj.time_spent
                          }
                          let finalUserObj = {};
                          finalUserObj["custid"] = custid;
                          finalUserObj["date"] = date;
                          finalUserObj["postid"] = item.postid;
                          finalUserObj["seen_time"] = item.time1;
                          finalUserObj["seen_unix_time"] = new Date(date + " " + item.time1).getTime();
                          if (result.getCategory != '') {
                            finalUserObj["category"] = result.getCategory.cat_name;
                            finalUserObj["post_desc"] = result.getCategory.post_desc;
                            finalUserObj["post_title"] = result.getCategory.post_title;
                            finalUserObj["langid"] = result.getCategory.langid;
                          }
                          finalUserObj["time_spent"] = finalPOstObj.time_spent
			//	console.log(finalUserObj)
                          localdb.collection(config.localMongodb.ratingCollection).updateOne({ custid: custid, postid: item.postid }, {
                            $set: finalUserObj
                            // , $push: { reaction: finalPOstObj } 
                          }, { upsert: true }, function (err, res) {
                            if (err) throw err;
                            itemCb()
                          })
                        } else {
                          itemCb()
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

              } else {
                releaseConn();
                asyncCb();
              }
            })
            //for iterating each post on that day and insert stats in db
            // async.forEachOf


          } else if (result && result.length == 0) {
            if (dateindex == (datesArr.length - 1)) {
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
    userCb({ new_last_post_date: new_last_post_date, new_last_post_time: new_last_post_time, time_spent_sum, new_total_posts });
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

