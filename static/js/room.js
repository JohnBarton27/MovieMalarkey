let userListElem = null;

let room = null;
let room_code = null;
let myUsername = null;
let userList = null;

function initSockets() {
    let socket = io();
    socket.on('connect', function() {
        socket.emit('join_room', { 'room': room_code });
    });

    socket.on('json', function(data) {
        if (data["event"] == "new-user") {
            setRoom(data['room']);
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

function updateUserList() {
    let userListHtml = '';
    $.each(room.users, function() {
        userListHtml += `<li>${this.name}</li>`;
    });
    userListElem.html(userListHtml);
}

function setRoom(inlineRoom) {
    room = inlineRoom;
    updateUserList();
}

$(document).ready(function() {
    // JQuery selectors
    userListElem = $("#userList");

    room_code = $("#room-data").data().code;

    myUsername = readCookie("user_name")
    initSockets();
});
