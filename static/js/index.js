let mainElem = null;
let nicknameElem = null;

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
    });
}

$(document).ready(function() {
    // JQuery selectors
    mainElem = $("#main");

    // On initial page load
    displayNicknamePrompt();
});
