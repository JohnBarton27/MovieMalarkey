let userListElem = null;

let room = null;
let room_code = null;
let myUsername = null;
let me = null;
let userList = null;
let startButtonElem = null;
let currentPlot = null;
let revealedGuesses = [];
let phase = null;  // Phases: JOINING, SELECTING, GUESSING, VOTING

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
            phase = "JOINING";
            setRoom(data['room']);
        } else if (data['event'] == "movie") {
            // Full Movie (for judge)
            displayTitle(data['title']);
            currentPlot = data['plot'];
            checkForStart(data['plot']);
        } else if (data['event'] == "movie-title") {
            // Title only (for players)
            phase = "GUESSING";
            displayTitle(data['title']);
            displayPlotInput();
        } else if (data['event'] == "user-answered") {
            setRoom(data['room']);
        } else if (data['event'] == "judge-selecting") {
            phase = "SELECTING";
            displayWaitingForJudge();
        } else if (data['event'] == 'user-guess') {
            setRoom(data['room']);

            // Update plot guesses table
            displayHostGuessesTable(room.movie.plot);
        } else if (data['event'] == 'all-guesses-submitted') {
            // All guesses have been submitted - we are almost ready to move to the "reading" phase
            phase = "VOTING";
            updateUserList(); // Remove 'checks' from usernames
            prepareForReading();
        } else if (data['event'] == 'guess-reveal') {
            revealGuessToAll(data['plot']);
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

    // User List
    $.each(room.users, function() {
        let isJudge = ``;
        let className = ``;
        let hasSubmitted = ``;

        if (this.name === room.judge.name) {
            // If this user is the judge
            isJudge = `<i class="fas fa-gavel"></i>`;
        }

        if (this.name === myUsername) {
            // If this is the current user
            className = `current-user`;
        }

        if (this.hasAnswered === "True" && phase === "GUESSING") {
            // If user has answered for the current round
            hasSubmitted = `<i class="fas fa-check"></i>`;
        }

        userListHtml += `<li class="${className}">${isJudge} ${this.name} ${hasSubmitted}</li>`;
    });
    userListElem.html(userListHtml);

    // "Start Game" Button
    if (room.started === 'False') {
        if (myUsername === room.host.name) {
            startButtonElem.html(`<button class="btn" onclick="startGame()">Start Game</button>`);
        } else {
            startButtonElem.html(`<span style="color:#e63946; padding: 5px; border-radius: 3px; border: 1px solid #e63946;">Waiting for host...</span>`);
        }
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

function checkForStart(plot) {
    let plotCheckHtml = `
        <p>${plot}</p>
        <hr>
        <p>Begin with this movie/plot?</p>
        <button onclick="begin();">Begin</button><button onclick="skipMovie();">Different Movie</button>
    `
    plotAreaElem.html(plotCheckHtml);
}

function begin() {
    $.post('/openGuesses');
    displayHostGuessesTable(currentPlot);
}

function skipMovie() {
    $.post('/startRound?code=' + room_code);
}

function displayHostGuessesTable(plot, revealButtons = false) {
    // Build table
    let guessesTable = `<table><tr><th>User</th><th>Guess</th><th>Reveal</th></tr>`;

    let revealButton = `disabled`;
    if (revealButtons) {
        revealButton = ``;
    }
    $.each(room.users, function() {
        guessesTable += `<tr><td>${this.name}</td>`;

        let btnHtml = `<button id="${this.name}-reveal-btn" ${revealButton} onclick="revealGuess('${this.name}');">Reveal</button>`;

        if (this.name === room.judge.name) {
            // The "judge" uses the real plot for their "answer"
            guessesTable += `<td>${plot}</td>
                <td>${btnHtml}</td></tr>`
        } else {
            // All other users have actual answers/guesses
            if (this.currentAnswer) {
                guessesTable += `<td>${this.currentAnswer}</td>
                    <td>${btnHtml}</td></tr>`;
            } else {
                guessesTable += `<td style="color: gray;">Waiting for answer...</td>
                    <td>${btnHtml}</td></tr>`;
            }
        }
    });

    guessesTable += `</table>`;
    plotAreaElem.html(guessesTable);
}

function displayGuessTable() {
    let guessesTable = `<table><tr><th>Guess</th><th>Vote</th></tr>`;

    $.each(revealedGuesses, function(index) {
        guessesTable += `<tr><td>${this}</td><td><button class="voteBtn" onclick="vote('${index}');">Vote!</button></td></tr>`;
    });

    guessesTable += `</table>`;

    plotAreaElem.html(guessesTable);
}

// Guesser submits a vote for the given plot
function vote(guessIndex) {
    // Disable all vote buttons (user can only vote once per round)
    $(".voteBtn").prop("disabled", true);

    $.ajax({
        url: '/vote',
        type: 'POST',
        data: {'guess': revealedGuesses[guessIndex]},
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
}

function revealGuess(username) {
    // Disable button to stop from revealing twice
    $("#" + username + "-reveal-btn").prop("disabled", true);

    // Send signal to server
    $.post('/revealGuess?username=' + username);
}

function lockInGuess(guess) {
    plotAreaElem.html(`<p>${guess}</p>`);
}

function displayPlotInput() {
    plotAreaElem.html(`<textarea id="plotGuess" rows="4" cols="50" style='display:block; margin:auto;'></textarea>
    <button class='btn' style='margin-top: 15px;' onclick="submitGuess()">Submit</btn>`);
}

function displayWaitingForJudge() {
    plotAreaElem.html(`<p>Waiting for judge to select a movie title/plot...</p>`);
}

function prepareForReading() {
    if (myUsername === room.judge.name) {
        // If this user is the judge, unlock the "reveal" buttons
        displayHostGuessesTable(room.movie.plot, revealButtons=true);
    } else {
        // Give guessers a message
        plotAreaElem.html(`<p>The judge is reading all responses - soon, you will vote on which you think is the real plot!</p>`);
    }
}

function revealGuessToAll(guess) {
    revealedGuesses.push(guess);

    if (myUsername !== room.judge.name) {
        displayGuessTable();
    }
}

function submitGuess() {
    let guess = $("#plotGuess").val();
    lockInGuess(guess);

    $.ajax({
        url: '/submitGuess',
        type: 'POST',
        data: {'guess': guess},
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function() {
            console.log("POSTed guess!");
        }
    });
}

function setRoom(inlineRoom) {
    room = inlineRoom;
    updateUserList();

    $.each(room.users, function() {
        if (this.name === myUsername) {
            me = this;
            return;
        }
    });

    if (room.movie && givenTitleElem.is(':empty')) {
        displayTitle(room.movie.title);
        if (myUsername === room.judge.name) {
            displayHostGuessesTable(room.movie.plot);
        }
    }
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