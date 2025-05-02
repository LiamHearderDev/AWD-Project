const test = "beans on toast";

const test2 = "Golden autumn leaves drift across the silent pond's surface, each ripple catching amber light as a lone heron glides overhead.";

const test3 = "Sunlight filtered through the high canopy of oak and maple, scattering golden patterns across the forest floor. A gentle breeze carried the scent of damp earth and wildflowers, while distant birdsong wove a delicate soundtrack through the trees. Beneath a fallen log, a family of salamanders stirred among the moss and decaying leaves, their slick bodies glinting in the dappled light. Nearby, a solitary mushroom unfurled its cap, releasing spores into the air like tiny drifting lanterns. Somewhere overhead, a squirrel chattered as it leapt from branch to branch in search of acorns. In this quiet woodland glade, time seemed to slow, inviting any wanderer to pause, breathe deeply, and marvel at nature’s subtle choreography.";

const gameId = 'gameElement';
const resultId = 'resultElement';
const timerId = 'timerElement';
const buttonId = 'startButton';
const gameContainerId = 'gameContainer';

function statistic(description, value) {
    this.description = description;
    this.value = value;
    this.toString = function() {
        return this.description + ': ' + this.value;
    };
}

function updateTimerDisplay(timerId, startTime) {
    const elapsed = (Date.now() - startTime) / 1000;
    $('#'+timerId).text(elapsed.toFixed(2) + ' s');
}

function callGame() {
    const $button = $('#' + buttonId);
    const $game = $('#' + gameContainerId);
    $button.css('display', 'none');
    $game.css('display', 'block');
    setupGame(gameId, resultId, timerId, test);
}

function setupGame(elementId, resultId, timerId, text) {
    // adds words to game element

    const $screen = $('#' + elementId).empty();
    $screen.off('keydown');

    let $current_word = $('<span></span>').appendTo($screen); // add first word

    for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        $('<span></span>') // add character to word
        .text(ch)
        .appendTo($current_word);

        if (ch === ' ') { // make new word
        $current_word = $('<span></span>').appendTo($screen);
        }
    }

    $screen.focus();

    startGame(elementId, resultId, timerId, text);
}

function startGame(elementId, resultId, timerId, text) {
    // starts game logic

    let $word = $('#' + elementId).children().eq(0);
    let $letter = $word.children().eq(0);
    let index = 0;
    const maxIndex = text.length-1;
    let mistakes = 0;

    let start = true;
    let startTime = 0;

    let stats = []
    let interval;

    $('#' + elementId).on('keydown', function (e) {
        const key = e.key;
        if ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,'".includes(key)) {
            if (start) { // start timer on first valid input
                startTime = Date.now();
                start = false;
                interval = setInterval(() => updateTimerDisplay(timerId, startTime), 10);
            }
            if (key === $letter.text()) { // style inputs accordingly with classes
                if ($letter.hasClass('wrong-char')) {
                    $letter.removeClass('wrong-char');
                }
                $letter.addClass('right-char');
            } else {
                if ($letter.hasClass('right-char')) {
                    $letter.removeClass('right-char');
                }
                $letter.addClass('wrong-char');
                mistakes += 1;
            }
            if ($letter.next().length === 0) { // signal to move on to next word
                if ($word.next().length === 0 && mistakes === 0) { // end of game if no more words
                    clearInterval(interval);
                    $('#' + elementId)
                        .off('keydown')
                    stats.push(new statistic('total characters', text.length));
                    stats.push(new statistic('total words', text.split(' ').length));
                    stats.push(new statistic('seconds to complete', ((Date.now() - startTime) / 1000)));
                    stats.push(new statistic('words per minute', Math.round((text.split(' ').length / ((Date.now() - startTime) / 60000)))));
                    stats.push(new statistic('characters per minute', Math.round((text.length / ((Date.now() - startTime) / 60000)))));
                    stats.push(new statistic('total mistakes', mistakes));
                    stats.push(new statistic('finished at', new Date().toLocaleTimeString()));
                    readResults(resultId, stats);
                    return;
                }
                else if ($word.next().length != 0) { // not end of game, move to next word
                    console.log("moving on to next word");
                    $word = $word.next();
                    $letter = $word.children().eq(0);
                }
                else if ($word.next().length === 0 && mistakes > 0) { // no more words but not end of game
                    console.log("no more words but not end of game");
                    index -= 1;
                }
            }
            else {
                $letter = $letter.next();
            }
            index += 1;
        } else if (key === 'Backspace' && index > 0) { // handle backspace
            if (!($word.next().length === 0 && mistakes > 0 && ($letter.hasClass('right-char') || $letter.hasClass('wrong-char')))) {
                console.log("backspace not at end");
                $letter = $letter.prev();
                if ($letter.length === 0) {
                    $word = $word.prev();
                    $letter = $word.children().last();
                }
                index -= 1;
            }
            else {
                console.log("backspace at end");
            }
            if ($letter.hasClass('right-char')) {
                $letter.removeClass('right-char');
            }
            if ($letter.hasClass('wrong-char')) {
                $letter.removeClass('wrong-char');
                mistakes -= 1;
            }
        }
        console.log("index: " + index);
        console.log("mistakes: " + mistakes);
        console.log("current word: " + $word.text());
        console.log("current letter: " + $letter.text());
    });
  }

function readResults(resultId, stats) {
    const $result = $('#' + resultId).empty();
    $result.css('display', 'block');
    const $list = $('<ul></ul>').appendTo($result);
    for (let i = 0; i < stats.length; i++) {
        const stat = stats[i];
        $('<li></li>')
            .text(stat.toString())
            .appendTo($list);
    }
    $list[0].scrollIntoView({ 
        behavior: 'smooth',  
        block: 'center'       
      });
    $list[0].focus();
}

 