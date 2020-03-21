'use strict';
module.exports = {
  sno : 0,
  _id : '0',
  event_id:'0',
  liveMongodb: {
    uri: "mongodb://49.156.128.103:27017/way2"
  },
  localMongodb : {
    // uri: "mongodb://nduser9:NeWs.7aWy2Nde@49.156.128.105:27017/way2",
    uri : "mongodb://localhost:27017/way2_personalize",
  
    userKeywordsCollection: "user_keywords_data_test",
    ratingCollection:"rating_points_test",
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
    hostname: '49.156.128.100',
    username: 'way2sms',
    password: 'waysmsawd#$%@',
    database: 'way2app',
    limit: 100,
    connectTimeout: 60 * 60 * 1000,
    acquireTimeout: 60 * 60 * 1000,
    timeout: 60 * 60 * 1000,
    queueLimit: 300,
    waitForConnections: true,
    autoReconnect: true
  },
  ratingPoints:{
    shares : 1,
    comments : 1,
    bookmark : 1,
    full_img_ad_points: 1,
    title_click : 1,
    screenshots: 1,
    post_spent_time_in_sec : 20,
    post_spent_time_points: 1,
    //for last post we dont have spent time we are giving 1 point below
    last_post_points : 1,
    video_click : 5,
    vide_play_time : 20,
    video_play_time_points : 2
  }
  // ratingPoints:{
  //   shares : 5,
  //   comments : 5,
  //   bookmark : 5,
  //   full_img_ad_points: 5,
  //   title_click : 5,
  //   screenshots: 5,
  //   post_spent_time_in_sec : 20,
  //   post_spent_time_points: 2,
  //   //for last post we dont have spent time we are giving 1 point below
  //   last_post_points : 1,
  //   video_click : 5,
  //   vide_play_time : 20,
  //   video_play_time_points : 2
  // }
};
