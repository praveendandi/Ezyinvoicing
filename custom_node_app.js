var fs = require('fs');
var path = require('path');
var socket = require('/home/caratred/frappe-bench/apps/frappe/node_modules/socket.io/lib/index.js');
// var socket = require('/home/frappe/frappe-bench/apps/frappe/node_modules/socket.io/lib/index.js')
// var express = require("/home/caratred/frappe_projects/Einvoice_Bench/apps/frappe/node_modules/express/index.js")
var express = require('/home/caratred/frappe-bench/apps/frappe/node_modules/express/index.js');
// var http = require('/home/caratred/Desktop/dpower/apps/frappe/node_modules/http/index.js')
var http = require('http')
var redis = require("/home/caratred/frappe-bench/apps/frappe/node_modules/redis/index.js");
var { get_conf, get_redis_subscriber } = require('/home/caratred/frappe-bench/apps/frappe/node_utils.js');

var conf = get_conf();

// var subscriber = redis.createClient(conf.redis_socketio || conf.redis_async_broker_port);
// alternatively one can try:
var subscriber = get_redis_subscriber();
const app = express();
const server = http.createServer(app);
const io = socket(server,{
    allowEIO3:true,
    cors:{
        origin:"*",
        method:['GET','POST']
    }
});
io.serveClient(true)
io.on('connection', (sock) => { 
    console.log('connect',sock.client.id)
    sock.emit('connect-me',"connected")
    // setInterval(()=>{
    //     io.emit('interval',"testing")
    // },1000)
 });
 io.on('connect_error', (err) => { 

 });
server.listen(process.argv[2]);
subscriber.on("message", function (channel, message) {
    // console.log("leyetettetetetetetetetetetetetet")
    message = JSON.parse(message);
    if (message.event == "custom_socket") {
        console.log("Got the Message:", message)
        io.emit('message',message)

    }
    // io.emit('message',"tetetetetetette")
});
subscriber.subscribe("events");

