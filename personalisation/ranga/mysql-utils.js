const mysql = require('mysql');
const config = require('./config/properties.json');

const dbsel = mysql.createPool({
    host : config.mysql.host,
    user : config.mysql.user,
    password : config.mysql.password,
    database : config.mysql.database,
    port : config.mysql.port,
    waitForConnections : config.mysql.waitForConnections,
    connectionLimit : config.mysql.connectionLimit
});

// const getConnection = () => {
//     return new Promise((resolve, reject) => {
//         dbsel.getConnection((err, con) => {
//             if(err) {
//                 reject(err);
//             } else {
//                 resolve(con);
//             }
//         })  
//     })
// }


function getConnection (mqcb){
    return new Promise((resolve, reject) => {
        dbsel.getConnection((err, con) => {
            if(err) {
                mqcb(err);
            } else {
                mqcb(null,con);
            }
        })  
    })
}

module.exports.getConnection = getConnection;