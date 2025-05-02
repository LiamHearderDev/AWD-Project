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

    startGame(elementId, resultId, timerId);
}

function startGame(elementId, resultId, timerId) {
    // starts game logic

    let $word = $('#' + elementId).children().eq(0);
    let $letter = $word.children().eq(0);
    let index = 0;
    let mistakes = 0;

    let start = true;
    let startTime = 0;

    stats = []

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
            $letter = $letter.next();
            if ($letter.length === 0) { // move to next word
                $word = $word.next();
                if ($word.length === 0) { // end of game if no more words
                    clearInterval(interval);
                    $('#' + elementId)
                        .off('keydown')
                    stats.push(new statistic('seconds to complete', ((Date.now() - startTime) / 1000)));
                    stats.push(new statistic('total characters', text.length));
                    stats.push(new statistic('total words', text.split(' ').length));
                    stats.push(new statistic('total mistakes', mistakes));
                    readResults(resultId, stats);
                    return;
                }
                $letter = $word.children().eq(0);
            }
            index += 1;
        } else if (key === 'Backspace' && index > 0) { // handle backspace
            $letter = $letter.prev();
            if ($letter.length === 0) {
                $word = $word.prev();
                $letter = $word.children().last();
            }
            if ($letter.hasClass('right-char')) {
                $letter.removeClass('right-char');
            }
            if ($letter.hasClass('wrong-char')) {
                $letter.removeClass('wrong-char');
            }
            index -= 1;
        }
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
    $list.scrollIntoView({ 
        behavior: 'smooth',  
        block: 'center'       
      });
    $list.focus();
}

 