let userListElem = null;

let room = null;
let room_code = null;
let myUsername = null;
let userList = null;
let startButtonElem = null;

let givenTitleElem = null;
let plotAreaElem = null;

function initSockets() {
    let socket = io();
    socket.on('connect', function() {
        socket.emit('join_room', { 'room': room_code });
    });

    socket.on('json', function(data) {
        if (data["event"] == "new-user") {
            setRoom(data['room']);
        } else if (data['event'] == "start-game") {
            setRoom(data['room']);
        } else if (data['event'] == "movie") {
            // Full Movie (for judge)
            displayTitle(data['title']);
            displayRealPlot(data['plot']);
        } else if (data['event'] == "movie-title") {
            // Title only (for players)
            displayTitle(data['title']);
            displayPlotInput();
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
        let isJudge = this.name === room.judge.name;
        userListHtml += `<li>${isJudge ? `<i class="fas fa-gavel"></i>` : ``} ${this.name}</li>`;
    });
    userListElem.html(userListHtml);

    if (room.started === 'False') {
        startButtonElem.html(`<button class="btn" onclick="startGame()">Start Game</button>`);
    } else {
        // Clear button if game has started
        startButtonElem.html(``);
    }
}

function startGame() {
    $.get('/startGame?code=' + room_code, function(responseText) {
        responseRoom = responseText;
        setRoom(responseRoom);
    });

}

function displayTitle(title) {
    givenTitleElem.html(`<h3>${title}</h3>`);
}

function displayRealPlot(plot) {
    plotAreaElem.html(`<p>${plot}</p>`);
}

function displayPlotInput() {
    plotAreaElem.html(`<textarea rows="4" cols="50"></textarea>`)
}

function setRoom(inlineRoom) {
    room = inlineRoom;
    updateUserList();
}

$(document).ready(function() {
    // JQuery selectors
    userListElem = $("#userList");
    startButtonElem = $("#startButton");
    givenTitleElem = $("#givenTitle");
    plotAreaElem = $("#plotArea");

    room_code = $("#room-data").data().code;

    myUsername = readCookie("user_name")
    initSockets();
});
