const test = "beans on toast";

function setupGame(elementId, text = test) {
    // reset screen
    const $screen = $('#' + elementId).empty();
    $screen.off('keydown');

    let $current_word = $('<span></span>').appendTo($screen); // add first word

    for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        $('<span></span>') // add character to word
        .text(ch === ' ' ? '\u00A0' : ch)
        .appendTo($current_word);

        if (ch === ' ') { // make new word
        $current_word = $('<span></span>').appendTo($screen);
        }
    }

    startGame(elementId);
}

function startGame(elementId) {
    let $word = $('#' + elementId).children().eq(0);
    let $letter = $word.children().eq(0);
    let index = 0;
    let mistakes = 0;

    let start = true;
    let startTime = 0;

    $('#' + elementId).on('keydown', function (e) {
        const key = e.key;
        if ("abcdefghijklmnopqrstuvwxyz ".includes(key)) {
            if (start) { // start timer on first valid input
                startTime = Date.now();
                start = false;
            }
            if (key === $letter.text()) { // colour inputs accordingly
                $letter.css('color', 'green');
            } else {
                $letter.css('color', 'red');
                mistakes += 1;
            }
            $letter = $letter.next();
            if ($letter.length === 0) { // move to next word
                $word = $word.next();
                if ($word.length === 0) { // end of game if no more words
                    $('#' + elementId)
                        .off('keydown')
                        .empty()
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
            $letter.css('color', 'black');
            index -= 1;
        }
    });
  }

 