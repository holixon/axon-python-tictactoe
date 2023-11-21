var board = Array(9).fill(0);
var symbols = ['o.png', 'blank.png', 'x.png'];

function refreshBoard(recs) {
    board.forEach(function (c, i) {
        var cell = document.getElementById('c' + i);
        cell.style.backgroundImage = 'url(assets/images/' + symbols[c + 1] + ')';
        if (recs[i] > 0) {
            cell.style.backgroundImage = 'radial-gradient(circle, green ' + Math.floor(80 * recs[i]) + '%, white, white)';
        } else if (recs[i] < 0) {
            cell.style.backgroundImage = 'radial-gradient(circle, red ' + Math.abs(Math.floor(80 * recs[i])) + '%, white, white)';
        } else {
            cell.style.backgroundColor = '#FFF';
        }
    });
}

async function postAPI(path, data, callback) {
    try {//http://localhost:8881
        const response = await fetch("" + path, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        callback(await response.json())
    } catch (error) {
        console.error("Error:", error);
    }
}

function play(action) {
    postAPI("/play", { id: id, action: action }, (result) => {
        sum = board.reduce((acc, e) => acc + Math.abs(e), 0);
        board[result.action] = sum % 2 == 0 ? 1 : -1;
        postAPI("/recommend", { state: board }, refreshBoard);
    })
}

function simulate() {
    const spinner = document.getElementById("spinner");
    spinner.style.display = "block";
    steps = document.getElementById("steps").value
    postAPI("/simulate", { "count": parseInt(steps) }, (result) => {
        spinner.style.display = "none";
        postAPI("/recommend", { state: board }, refreshBoard);
    });
}