let mainElem = null;
let nicknameElem = null;
let roomCodeElem = null;
let roomNotFoundElem = null;

function displayNicknamePrompt() {
    let nicknameId = "nickname";
    mainElem.html(`
        <label for="${nicknameId}">Enter nickname:</label>
        <input id="${nicknameId}" name="Nickname" type="text"/>
        <button onclick="submitName();">Submit</button>
    `);
    nicknameElem = $("#" + nicknameId);
}

function submitName() {
    $.post("/roomSearch?nickname=" + nicknameElem.val(), function(responseText) {
        mainElem.html(responseText);
        roomCodeElem = $("#room-code");
        roomNotFoundElem = $("#roomNotFound")
    });
}

function createRoom() {
    $.post("/newRoom", function(responseText) {
        let room_code = responseText;
        window.location.href = '/play';
    });
}

function searchRoom() {
    let roomCode = roomCodeElem.val();
    $.get('/checkRoomCode?code=' + roomCode, function(responseText) {
        if (responseText === 'true') {
            roomNotFoundElem.html('');
            window.location.href = '/play';
        } else {
            roomNotFoundElem.html(`Could not find room with code ${roomCode}!`);
        }
    });
}

$(document).ready(function() {
    // JQuery selectors
    mainElem = $("#main");

    // On initial page load
    displayNicknamePrompt();
});
