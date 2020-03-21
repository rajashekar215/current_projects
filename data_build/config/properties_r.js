'use strict';
module.exports = {
  sno : 0,
  _id : '0',
  event_id:'0',
  liveMongodb: {
    uri: "mongodb://103.248.83.227:27017/way2?readPreference=secondaryPreferred"
  },
  localMongodb : {
    // uri: "mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2",
    uri : "mongodb://w2nai_local_admin:w2naimongoadmin@localhost:27017/user_word_cloud?authSource=admin",
    testing_users:"november_active_users",
    userKeywordsCollection: "user_keywords_data_testing_users",
    ratingCollection:"rating_points_testing_users",
    activesCollection:"active_users_test",
    userDataCollection: "user_data_new_test",
    userLastPost: "user_last_post_test",

    
    postDataCollection : "posts_data",
    custIdCollection  : "custids_data_test",
    testing_collection:"testing_collection"
  },
  // localMongodb : {
  //   // uri: "mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2",
  //   uri : "mongodb://localhost:27017/way2",
  
  //   userKeywordsCollection: "newsreg-user-keywords-data",
  //   ratingCollection:"newsreg-rating_points",
  //   activesCollection:"newsreg-active-users",
  //   userDataCollection: "newsreg-user-data",
  //   userLastPost: "newsreg-user-last-post",

    
  //   postDataCollection : "newsreg-posts-data",
  //   custIdCollection  : "newsreg-custids"
  // },

  //mysql properties
  databasesel: {
    hostname: '192.168.1.98',
    username: 'way2sms',
    password: 'waysmsawd#$%@',
    database: 'way2app',
    connectionLimit:2000,
    limit: 2000,
    connectTimeout: 60 * 60 * 1000,
    acquireTimeout: 60 * 60 * 1000,
    timeout: 60 * 60 * 1000,
    queueLimit: 3000,
    waitForConnections: true,
    autoReconnect: true
  },
  ratingPoints:{
    shares : 4,
    push_open : 4,

    comments : 3,
    likeclick_one : 3,


    bookmark : 2,
    full_img_ad_points: 2,
    picdownload : 2,
    title_click : 2,
    screenshots: 2,
    // video_click : 2,

    post_spent_time_points: 1,
    video_play_time_points : 1,

    notification_clear : 0,

    // category_click :1,
    // topbuzz_click : 1,

    post_spent_time_in_sec : 20,
    vide_play_time : 20

  }
};
