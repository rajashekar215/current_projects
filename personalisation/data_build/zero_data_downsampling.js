const MongoClient = require('mongodb').MongoClient;
const async = require('async');
const dateTime = require('node-datetime');
var moment = require("moment")
const mongo = require('mongodb');
var request = require('request');

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

var cat_array=[
    'crime general security sports',
    'birthday central',
    'general',
'general state',
'state',
'crime security',
'general movie',
'crime general security',
'central general',
'movie',
'education general',
'general religious',
'environmnet general',
'religious',
'cricket general sports',
'central state',
'agriculture general projects',
'general health',
'movie state',
'environmnet',
'birthday',
'general state',
'crime security state',
'movie state',
'central',
'birthday general',
'crime security state',
'cricket sports',
'crime movie security',
'business stocks',
'education movie',
'business general stocks',
'education state',
'central movie',
'climate general',
'health',
'central movie',
'education state',
'cricket movie sports',
'environmnet state',
'education',
'central general',
'environmnet state',
'central crime security',
'agriculture projects',
'cricket cricket sports sports',
'religious state',
'health state',
'religious state',
'health movie',
'agriculture projects state',
'central crime security',
'health state',
'agriculture projects state',
'movie religious',
'general general sports',
'cricket sports state',
'crime education security',
'election general',
'education environmnet',
'cricket sports state',
'business central stocks',
'general movie sports',
'agriculture movie projects',
'general media social',
'cricket general sports sports',
'crime environmnet security',
'general technology',
'environmnet health',
'election state',
'crime health security',
'central education',
'crime religious security',
'cricket crime security sports',
'central cricket sports',
'agriculture crime projects security',
'central cricket sports',
'central education',
'media movie social',
'agriculture central projects',
'environmnet movie',
'climate crime security',
'education health',
'agriculture central projects',
'business central stocks',
'election movie',
'agriculture business projects stocks',
'business movie stocks',
'climate',
'business state stocks',
'general sports state',
'central health',
'central environmnet',
'election state',
'agriculture climate projects',
'environmnet religious',
'cricket media social sports',
'agriculture environmnet projects',
'central environmnet',
'central health',
'central religious',
'business state stocks',
'climate movie',
'central religious',
'climate state',
'agriculture health projects',
'crime media security social',
'central central',
'birthday movie',
'media social state',
'agriculture cricket projects sports',
'education religious',
'climate state',
'crime election security',
'general health sports',
'general research',
'general sports state',
'central technology',
'education general sports',
'business crime security stocks',
'central climate',
'media social state',
'central general sports',
'state technology',
'religious technology',
'technology',
'business cricket sports stocks',
'climate cricket sports',
'central election',
'birthday crime security',
'agriculture projects religious',
'central climate',
'health religious',
'central election',
'election environmnet',
'birthday state',
'education election',
'business health stocks',
'movie technology',
'general sports',
'crime research security',
'cricket election sports',
'central general sports',
'agriculture general projects sports',
'cricket education sports',
'central media social',
'business education stocks',
'religious technology',
'movie technology',
'climate environmnet',
'birthday state',
'research state',
'cricket health sports',
'election health',
'agriculture media projects social',
'central media social',
'movie research',
'birthday climate',
'general technology',
'climate religious',
'cricket religious sports',
'general religious sports',
'media social',
'central research',
'climate education',
'agriculture education projects',
'climate media social',
'cricket environmnet sports',
'birthday central',
'election',
'climate health',
'research state',
'business general sports stocks',
'climate election',
'birthday cricket sports',
'birthday religious',
'crime security technology',
'environmnet general sports',
'birthday education',
'cricket research sports',
'business religious stocks',
'agriculture birthday projects',
'birthday health',
'health research',
'central research',
'business environmnet stocks',
'business election stocks',
'climate research',
'election general sports',
'election religious',
'agriculture projects research',
'media religious social',
'health technology',
'health technology',
'business stocks technology',
'climate general sports',
'business media social stocks',
'environmnet research',
'general media social sports',
'general sports technology',
'education media social',
'environmnet media social',
'birthday technology',
'crime security technology',
'climate technology',
'general sports technology',
'media research social',
'birthday environmnet',
'agriculture election projects',
'birthday general sports',
'climate technology',
'education technology',
'birthday election',
'education research',
'business stocks technology',
'cricket sports technology',
'education technology',
'birthday media social',
'business climate stocks',
'election research',
'research']



MongoClient.connect("mongodb://localhost:27017", {useNewUrlParser: true}, function (err, localclient) {
            if (err) {
                console.log(err);
                // reject(err)
            } else {
                const localdb = localclient.db('way2viral');
                function fone(cat,fcb){
                    console.log(cat," is in process")
                    localdb.collection("virality_all_data").find({new_cat:cat,target:0,train:null}).toArray(function(err,docs){
                        if(docs && docs.length){
                            console.log(cat,docs.length)
                            // process.exit()
                            let did=docs[0]["_id"]
                            let d1=docs[0]["text"]
                            docs.splice(0,1)
                            async.forEachLimit(docs,100, function (doc, gcb) {
                                let d2=doc["text"]
                                request.post(
                                    'http://49.156.128.11:5005/simapi',
                                    { json:  data = {"lang": "Telugu", "text1":d1, "text2":[d2],"le":1}  },
                                    function (error, response, body) {
                                        if (!error && response.statusCode == 200) {
                                            console.log(cat," body",body);
                                            if(body["simlist"] && body["simlist"][0]){
                                                console.log("text1  ",d1)
                                                console.log("text2  ",d2)
                                                localdb.collection("virality_all_data").updateOne({_id:doc._id},{$set:{train:0}},function(){
                                                    gcb();
                                                })
                                            }else{
                                                gcb();
                                            }
                                        }else{
                                            console.log("err",body)
                                        }
                                    }
                                );
                            },function(){
                                localdb.collection("virality_all_data").updateOne({_id:did},{$set:{train:1}},function(){
                                    // gcb();
                                    fone(cat,function(){
                                        fcb();
                                    })
                                })
                            })
                        }else{
                            fcb();
                        }
                        
                    })
                }


                // let cat="agriculture central projects"
                //     fone(cat,function(){
                //         console.log(cat," data completed")
                //         // cb()
                //     })                
                async.eachSeries(cat_array, function (cat, cb) {
                    fone(cat,function(){
                        cb()
                    })                    
                },function(){
                        console.log("all categories completed")
                })


            }
        })
