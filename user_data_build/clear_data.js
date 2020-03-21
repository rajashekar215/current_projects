const async = require("async");
const mongo = require('mongodb');
const MongoClient = require('mongodb').MongoClient;

function connectDB(cb) {
  MongoClient.connect("mongodb://localhost:27017/user_word_cloud", function (err, localdb) {
    cb(err, localdb)
  })
}

function remove_data(skip, err, localdb) {
  if (localdb != null) {
    localdb.collection("rating_points_testing_users").find({
      // custid:21343349,
      //rating: { $in: [0, null] }
      date:{$lt:"2020-01-01"}
    }).skip(skip).limit(1000).toArray(function (err, docs) {
      if (!err && docs) {
        // console.log(docs)
        if (docs.length > 0) {
          console.log("testing custids fetched from mongo:: ", docs.length)
          let to_skip = 0
          async.forEach(docs, function (doc, cb) {

            if (doc.seen_unix_time < 1577817000000) {
              console.log(doc._id)
              localdb.collection("rating_points_testing_users").remove({ _id: doc._id }, function () {
                cb()
              })
            } else {
              to_skip++
              console.log("january doc ", doc._id, skip)
              cb()
            }
          }, function () {
            setTimeout(function () {
              remove_data(skip + to_skip, err, localdb)
            }, 0)
          })
        }
        else {
          console.log("no data")
        }
      } else if (err) {
        console.log(err)
        connectDB(function (err, localdb) {
          setTimeout(function () {
            remove_data(skip + to_skip, err, localdb)
          }, 0)
        })
      }
    })
  } else {
    console.log(err)
    connectDB(function (err, localdb) {
      setTimeout(function () {
        remove_data(skip + to_skip, err, localdb)
      }, 0)
    })
  }
}
connectDB(function (err, localdb) {

  remove_data(0, err, localdb)
})