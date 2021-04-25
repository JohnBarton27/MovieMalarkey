let userListElem = null;

let room = null;
let myUsername = null;

function initSockets() {
    let socket = io();
    socket.on('connect', function() {
        socket.emit('join_room', { room: room.code});
    });

    socket.on('json', function(data) {
        if (data["event"] == "new-user" && data["username"] != myUsername) {
            userListElem.append(`<li>${data["username"]}</li>`);
        }
    });
}

function readCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

$(document).ready(function() {
    // JQuery selectors
    userListElem = $("#userList");

    myUsername = readCookie("user_name")
    room = $("#room-data").data();
    initSockets();
});
