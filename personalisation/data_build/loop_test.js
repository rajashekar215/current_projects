// const async = require('async');
// l=[1,2,3,4,5,6,7,8]
// async.forEach(l, function (doc, gcb) {
//     l.splice(l.indexOf(doc),1)
//     console.log(l)
// },function(){})

var splitArray = require('split-array');
let sa=splitArray(['a', 'b', 'c', 'd', 'e', 'f'], 3);
console.log(sa)