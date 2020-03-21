'use strict';
var config = require('../config/properties');
var mysql = require('mysql');
var pool = mysql.createPool({
  connectionLimit: config.databasesel.limit,
  host: config.databasesel.hostname,
  user: config.databasesel.username,
  password: config.databasesel.password,
  database: config.databasesel.database,
  connectTimeout: config.databasesel.connectTimeout,
  aquireTimeout: config.databasesel.acquireTimeout,
  timeout: config.databasesel.timeout,
  queueLimit: config.databasesel.queueLimit,
  waitForConnections: config.databasesel.waitForConnections,
  autoReconnect: config.databasesel.autoReconnect,
  debug: false
});
module.exports = pool;
