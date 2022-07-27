var fs = require('fs');
var path = require('path');

// var socket = require('/home/caratred/frappe/frappe_bench/apps/frappe/node_modules/socket.io/lib/index.js')

var socket = require('socket.io')

// var express = require('/home/caratred/frappe/frappe_bench/apps/frappe/node_modules/express/index.js')
var express = require("express")

// var http = require('/home/caratred/Desktop/dpower/apps/frappe/node_modules/http/index.js')
var http = require('http')
// var redis = require("/home/caratred/frappe/frappe_bench/apps/frappe/node_modules/redis/index.js");
var redis = require("redis");

// var { get_conf, get_redis_subscriber } = require('/home/caratred/frappe/frappe_bench/apps/frappe/node_utils.js');
var { get_conf, get_redis_subscriber } = require('../frappe/node_utils.js');


// const axios = require("/home/caratred/frappe/frappe_bench/apps/frappe/node_modules/axios/index.js");
const axios = require("axios")
var conf = get_conf();

// var subscriber = redis.createClient(conf.redis_socketio || conf.redis_async_broker_port);
// alternatively one can try:
var subscriber = get_redis_subscriber();
const app = express();
const HttpsProxyAgent = require('https-proxy-agent');


const server = http.createServer(app);


const io = socket(server);
let users = []
io.on('connection', (client) => {
    console.log('connect', client.client.id)
    users.push(users)
    client.on('host_emitter', (data) => {
        // io.emit('host_listner', data)
        io.to(data.work_station_id).emit('host_listner', data);
    })
    client.emit('connected', { "client": client.client.id });
    console.log('connect_host', client.client.id)
    client.on('disconnect', function (data) {
        // console.log("disconnect", client.client.id,"&&&&&&&&&&&&&&&777")
        io.emit('station_disconnected', client.client.id)
        removeWorkStation(client.client.id);
        removeTablet(client.client.id);
        // io.emit('station_disconnected',client.client.id)

    });
});


io.on('workstation_connection', function (data) {
    console.log(data)
});


subscriber.on("message", function (channel, message) {
    // console.log("leyetettetetetetetetetetetetetet")
    message = JSON.parse(message);
    if (message.event == "custom_socket") {
        // console.log("Got the Message:", message)
        if (message.message.message == "Tablet Mapped") {
            // console.log("tablet mapped",message.message.data.work_station,message.message.data.tablet)
            // console.log("tablet mapped workstaion",message.message.data.work_station)
            // console.log("tablet mapped tablet",message.message.data.tablet)
            console.log("Tablet mapped", message.message.data.work_station_socket_id, message.message.data.tablet_socket_id)
            io.to(message.message.data.work_station_socket_id).emit('message', message);
            io.to(message.message.data.tablet_socket_id).emit('message', message);
            // message.message.data.work_station
        }
        else if (message.message.message == "Tablet Config Disconnected") {
            if (message.message.data.doctype == 'Tablet Config') {
                // console.log("Got the Message:", message)
                // console.log("work station:", message.message.data.work_station)
                io.to(message.message.data.work_station_socket_id).emit('message', message);
            }
            // console.log("work station:", message.message.data.work_station)
            // console.log("work station:", message.message.data.tablet)
            // console.log("work station:", message.message.data)

            io.to(message.message.data.tablet).emit('message', message);
            // message.message.data.work_station
        }
        else if (message.message.message == "Push To Tab") {
            // io.to(message.message.data.work_station).emit('message', message);
            // io.emit('message', message);
            console.log("tablet_socket_id", message)
            io.to(message.message.data.tablet_config.tablet_socket_id).emit('message', message);

            console.log("tablet_socket_id", message.message.data.tablet_config.tablet_socket_id)
            // message.message.data.work_station
        }
        else if (message.message.message == 'Signature Updated') {
            io.to(message.message.data.work_station_socket_id).emit('message', message);
        }
        // else if (message.message.message == 'Disconnect Tablet') {
        //     console.log(message.message.data.tablet_socket_id)
        //     io.to(message.message.data.tablet_socket_id).emit('message', message);
        // }
        else {
            // console.log("*************************************")
            io.emit('message', message)
            // console.log(message)
        }
    }
    // io.emit('message', "tetetetetetette")
});
subscriber.subscribe("events");

/* ------------------ remove work station after disconnect socket --------------*/

let removeWorkStation = socket_id => {
    try {
        // axios.delete(`http://0.0.0.0:8000/api/resource/Active Work Stations/${socket_id}`)
        axios.post(`http://0.0.0.0:8000/api/method/version2_app.version2_app.doctype.active_work_stations.active_work_stations.removeWorkstation`, { name: socket_id })
            .then(res => res.json())
            .then(res => res)
            .catch(err => console.log("error"))
            .catch(err => console.log("error"))

        console.log(socket_id, "for remove")
    } catch (e) {
        console.log(e, "this is error")
    }
}

let removeTablet = socket_id => {
    try {
        // axios.delete(`http://0.0.0.0:8000/api/resource/Active Tablets/${socket_id}`)
        axios.post(`http://0.0.0.0:8000/api/method/version2_app.version2_app.doctype.active_tablets.active_tablets.removeTab`, { name: socket_id })
            .then(res => res.json())
            .then(res => res)
            .catch(err => console.log("error"))

        console.log(socket_id, "for remove")
    } catch (e) {
        console.log(e, "this is error")
    }
}




//socket client connection

const client_io = require('socket.io-client');
let client_socket
let license_server = 'http://localhost:3000'
const connet_socket_server = async function () {
    let company_settings = 'http://0.0.0.0:8001/api/resource/company'
    let company_resp = await axios.get(`${company_settings}`)
    console.log(company_resp.data)
    // '[["name","=","HICC-01"]]&fields=["name"]'
    let company_details_api = `http://0.0.0.0:8001/api/resource/company?filters=[["name","=","${company_resp.data.data[0].name}"]]&fields=["name","proxy","proxy_url","proxy_username","proxy_password"]`
    console.log(company_details_api)
    company_details = await axios.get(`${company_details_api}`)
    console.log(company_details.data)
    if (company_details.data == 1) {
        let url = `http://${company_details.data.data.proxy_username}:${company_details.data.data.proxy_password}@$${company_details.data.data.proxy_url}`
        let agent = new HttpsProxyAgent(url);
        let opts = {
            secure: true,
            rejectUnauthorized: false,
            reconnect: true,
            agent: agent
        };
        client_socket = client_io.connect(license_server, opts);

    } else {
        client_socket = client_io.connect(license_server, {
            reconnection: true
        });
        // console.log(client_socket.id)
        connect(client_socket, company_resp)
        // 
    }

}

const connect = async function (socket, company_resp) {
    socket.on('connect', async function () {
        console.log('connected to socket server');
        client_socket.emit('connect_property', { "hotel_code": company_resp.data.data[0].name })
    })
}

setTimeout(() => {
    connet_socket_server()
}, 1000)







let remove = async function () {
    try {
        console.log("hiee")
        // axios.delete(`http://0.0.0.0:8000/api/resource/Active Tablets/${socket_id}`)
        // await axios.post(`http://0.0.0.0:8000/api/method/version2_app.version2_app.doctype.tablet_config.tablet_config.removeAllDevices`)
        process.exit()
    } catch (e) {
        console.log(e, "this is error")
    }
}

process.stdin.resume();//so the program will not close instantly

function exitHandler(options, exitCode) {
    // if (options.cleanup) {
    //     remove()
    //     console.log('clean')};
    // if (exitCode || exitCode === 0) console.log(exitCode);
    // if (options.exit) process.exit();
    // remove()
}

//do something when app is closing
process.on('exit', exitHandler.bind(null, { cleanup: true }));

//catches ctrl+c event
process.on('SIGINT', exitHandler.bind(null, { exit: true }));

// catches "kill pid" (for example: nodemon restart)
process.on('SIGUSR1', exitHandler.bind(null, { exit: true }));
process.on('SIGUSR2', exitHandler.bind(null, { exit: true }));

//catches uncaught exceptions
process.on('uncaughtException', exitHandler.bind(null, { exit: true }));
server.listen(5001);









