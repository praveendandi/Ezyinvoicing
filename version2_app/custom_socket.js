const redis = require("redis");
 
var config = {
    port: 9200,
    // secret: 'secret',
    
    redisConf: {
    host: '0.0.0.0', // The redis's server ip 
    port: '9200',
    pass: 'theredispass'
    }
    };
const subscriber = redis.createClient(config);
// const publisher = redis.createClient();
 
let messageCount = 0;
console.log(subscriber)
subscriber.on("subscribe", function(channel, count) {
//   publisher.publish("a channel", "a message");
//   publisher.publish("a channel", "another message");
});
 
subscriber.on("message", function(channel, message) {
  messageCount += 1;
 
  console.log("Subscriber received message in channel '" + channel + "': " + message);
 
  if (messageCount === 2) {
    subscriber.unsubscribe();
    subscriber.quit();
    publisher.quit();
  }
});
 
subscriber.subscribe("a channel");