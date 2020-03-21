var mysql = require('./mysql-utils');
const fs = require('fs');
const config = require('./config/properties.json');
const MongoClient = require('mongodb').MongoClient;
const splitArray = require('split-array')
const async = require('async');
const moment = require('moment')

const url = "mongodb://localhost:27017";
const coll = "english_words_collection"
let db;
// const client = await getMongoConn()
// let conn = await getConnection();
// const main = async (date) => {

function purify(keyword,kcb){
    let newkeyword = keyword.replace(/(\r\n|\n|\r|\s|\.$|^\.|^,|,$|^'|'$|^"|"$|^:|:$|^\?|\?$|‘|’|^<|<$|^>|>$|^&|&$)/gm, "").trim();
    if(newkeyword.match(/(\r\n|\n|\r|\s|\.$|^\.|^,|,$|^'|'$|^"|"$|^:|:$|^\?|\?$|‘|’|^<|<$|^>|>$|^&|&$)/gm)){
        purify(newkeyword,function(newkey){
           kcb(newkey)
        })
    }else{
        kcb(newkeyword)
    }
}

function main(date,client,conn,mcb){
    try {

        
        const db = client.db('way2');

        //let day_start_time = parseInt(new Date().setHours(0, 0, 0) / 1000);
        //let day_end_time = parseInt(new Date().setHours(23, 59, 59) / 1000);

        let day_start_time = parseInt(new Date(date).setHours(0, 0, 0) / 1000);
        let day_end_time = parseInt(new Date(date).setHours(23, 59, 59) / 1000);

        let qry = "select post_desc from mag_posts_home_new where post_desc is not null and lang_id = ? and post_status = ? and post_gmt between ? and ? ";
        let prms = [];
        prms.push(11);
        prms.push('published');
        prms.push(day_start_time);
        prms.push(day_end_time);

        
        // let res = await executeQry(conn, 'select', qry, prms);
        executeQry(conn, 'select', qry, prms,function(err,res){
            if(!err && res){
                console.log(res.length);

                //console.log(res);
        
                //res = res.slice(0, 2);
        
        
                async.each(res,function(row,cb){
                    if(!row["post_desc"])
                        console.log(row)
                    let pdes=row["post_desc"].replace(/(\r\n|\n|\r|>|\s|\(|\)|\*)/gm, " ")
                    let arrWords = pdes.split(' ');
                    async.each(arrWords,function(keyword,rcb){

                        if(keyword.match(/(\r\n|\n|\r|\s|\.$|^\.|^,|,$|^'|'$|^"|"$|^:|:$|^\?|\?$|‘|’|^<|<$|^>|>$|^&|&$)/gm)){
                            purify(keyword,function(newkey){
                                keyword=newkey
                            })
                        } 
                            if (!keyword.match(/\d/) && keyword!="") {
                                // keyword = keyword.replace(/(\r\n|\n|\r|>|\s|\.$|\^.|^,|,$|^'|'$|^"|"$)/gm, "").trim();
                                db.collection(coll).updateOne({ _id: keyword }, { $inc: { count: 1 } }, { upsert: true }, (err, mongoRes) => {
            
                                    if (err) {
                                        // throw err;
                                        db.collection(coll).updateOne({ _id: keyword }, { $inc: { count: 1 } }, (err, mongoRes) => {
            
                                            if (err) {
                                                throw err;
                                            }else{
                                                rcb();
                                            }
                                        })
                                    }else{
                                        rcb();
                                    }
                                })
                            } else if(keyword!="") {
                                db.collection("english_num_words").updateOne({ _id: keyword }, { $inc: { count: 1 } }, { upsert: true }, (err, mongoRes) => {
            
                                    if (err) {
                                        db.collection("english_num_words").updateOne({ _id: keyword }, { $inc: { count: 1 } },  (err, mongoRes) => {
            
                                            if (err) {
                                                throw err;
                                            }else{
                                                rcb();
                                            }
                                        })
                                    }else{
                                        rcb();
                                    }
                                })
                            }else{
                                rcb();
                            }
                        
                        
                    },function(){
                        cb()
                    })
                },function(){
                    // client.close();
                    // console.log(res);
                    console.log(date+"  all are done");
                    mcb();
                })
            }else{
                console.log(err)
            }
        });

        


        // for await (row of res) {
        //     // console.log("hiii")
        //     let arrWords = row["post_desc"].split(' ');
        //     for await (word of arrWords) {
        //         let keyword = word.replace(/(\r\n|\n|\r|>|\s)/gm, " ").trim();
        //         if (!keyword.match(/\d|[a-zA-Z]/)) {
        //             db.collection(coll).updateOne({ _id: keyword }, { $inc: { count: 1 } }, { upsert: true }, (err, mongoRes) => {

        //                 if (err) {
        //                     throw err;
        //                 }
        //             })
        //         } else {
        //             db.collection("num_words").updateOne({ _id: keyword }, { $inc: { count: 1 } }, { upsert: true }, (err, mongoRes) => {

        //                 if (err) {
        //                     throw err;
        //                 }
        //             })
        //         }
        //     }
        //     // let done = fs.appendFileSync(config.file_name, row.post_desc);
        //     // console.log('append done ', done);
        // }

        // console.log(`${100} records are done`);



       

    } catch (err) {
        throw err;
    }
}

const getMongoConn = () => {
    return new Promise((resolve, reject) => {

        MongoClient.connect(url, { useNewUrlParser: true }, (err, client) => {
            if (err) {
                console.log(err);
                reject(err)
            }
            resolve(client)
        })
    })

}

const doInsert = (res) => {
    return new Promise((resolve, reject) => {
        let a = fs.writeSync(config.file_name, res, 'utf-8', (err, res) => {
            if (err) {
                reject(err)
            } else {
                resolve("file successfully created");
            }
        })
    })
}

const getConnection = async () => {

    try {
        const conn = await mysql.getConnection();
        return conn;
    } catch (e) {
        throw e;
    }

}
// const executeQry = (conn, type, qry, params) => {

//     return new Promise((resolve, reject) => {
//         if (type === 'select') {
//             console.log(qry, params);

//             conn.query(qry, params, (err, res) => {
//                 // console.log(res);
//                 conn.release();

//                 if (err) {
//                     reject(err);
//                 } else {
//                     resolve(res);
//                 }
//             })
//         } else {
//             reject('Invalid qry operation');
//         }

//     })

// }

function executeQry(conn, type, qry, params,ecb) {

    if (type === 'select') {
        console.log(qry, params);

        conn.query(qry, params, (err, res) => {
            // console.log(res);
            conn.release();

            if (err) {
                ecb(err,res);
            } else {
                ecb(err,res);
            }
        })
    } else {
        ecb('Invalid qry operation');
    }
}





buildDataKeywords = () => {

    let arr = generateDates(90, null);
    async.eachSeries(arr, (date, AsyncCb) => {
        console.log(date)
        MongoClient.connect(url, { useNewUrlParser: true }, (err, client) => {
            if (err) {
                console.log(err);
                // reject(err)
            }else{
                console.log("got mongo")
                client=client
                mysql.getConnection(function(err,mqres){
                    if(!err && mqres){
                        console.log("got mysql")
                        conn=mqres
                        main(date,client,conn,function(){
                            console.log(date+" done");
                            client.close();
                            // conn.release();
                                AsyncCb();
                        })
                    }else{
                        console.log(err)
                    }
                })
        
                
            }
        })
        



        

        
    },function(success) {
        console.log("#############################");
    })
    // async.eachSeries(arr, (date, AsyncCb) => {
    //     console.log(date)
    //     main(date)
    //         .then((response) => {
    //             console.log(response);
    //             AsyncCb();
    //         })
    //         .catch(err => console.log('error is  ', err));
    // },function(success) {
    //     console.log("#############################");
    // })

}
buildDataKeywords();

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
    if (dd < 10) { dd = '0' + dd }
    if (mm < 10) { mm = '0' + mm };
    return d = yyyy + '-' + mm + '-' + dd;
}

