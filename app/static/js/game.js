const test = "beans on toast";

const test2 = "Golden autumn leaves drift across the silent pond's surface, each ripple catching amber light as a lone heron glides overhead.";

const test3 = "Sunlight filtered through the high canopy of oak and maple, scattering golden patterns across the forest floor. A gentle breeze carried the scent of damp earth and wildflowers, while distant birdsong wove a delicate soundtrack through the trees. Beneath a fallen log, a family of salamanders stirred among the moss and decaying leaves, their slick bodies glinting in the dappled light. Nearby, a solitary mushroom unfurled its cap, releasing spores into the air like tiny drifting lanterns. Somewhere overhead, a squirrel chattered as it leapt from branch to branch in search of acorns. In this quiet woodland glade, time seemed to slow, inviting any wanderer to pause, breathe deeply, and marvel at nature’s subtle choreography.";

const gameId = 'gameElement';
const resultId = 'resultElement';

function setupGame(elementId, resultId, text = test) {
    // reset screen
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

    startGame(elementId, resultId);
}

function startGame(elementId, resultId) {
    let $word = $('#' + elementId).children().eq(0);
    let $letter = $word.children().eq(0);
    let index = 0;
    let mistakes = 0;

    let start = true;
    let startTime = 0;

    $('#' + elementId).on('keydown', function (e) {
        const key = e.key;
        if ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,'".includes(key)) {
            if (start) { // start timer on first valid input
                startTime = Date.now();
                start = false;
            }
            if (key === $letter.text()) { // colour inputs accordingly
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
                    $('#' + elementId)
                        .off('keydown')
                    $('#' + resultId)
                        .css('display', 'block')
                        .text('You finished in ' + ((Date.now() - startTime) / 1000).toFixed(2) 
                                + ' seconds with ' + mistakes + ' mistakes.');
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

  document.addEventListener('DOMContentLoaded', function() {
    setupGame(gameId, resultId, test);
  });
 