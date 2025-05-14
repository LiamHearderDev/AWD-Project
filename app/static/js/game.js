const placeholder = "placeholder text, paragraph was not loaded correctly";

const gameId = 'gameElement';
const resultId = 'resultElement';
const timerId = 'timerElement';
const buttonId = 'startButton';
const gameContainerId = 'gameContainer';

const csrfToken = document.querySelector('meta[name="csrf-token"]').content; // get csrf token from header
$.ajaxSetup({ // makes so that all future AJAX communications to server add CSRF automatically
    headers: { 'X-CSRFToken': csrfToken }
});

function statistic(description, value) { // constructor for statistics
    this.description = description;
    this.value = value;

    this.toJSON = function() { // turn to JSON for sending data to server
        return {
            description: this.description,
            value: this.value
        };
    };

    this.toString = function() { // turn to string for displaying data
        if (this.value && typeof this.value === 'object' && !Array.isArray(this.value)) { // for dictionary like objects
            const formatted = Object.entries(this.value)
                .map(([k, v]) => `${k}: ${v}`)
                .join(', ');
            return `${this.description}: ${formatted}`;
        }
        return `${this.description}: ${this.value}`;
    };
}


function updateTimerDisplay(timerId, startTime) { // function to update timer display, is used in setInterval
    const elapsed = (Date.now() - startTime) / 1000;
    $('#'+timerId).text(elapsed.toFixed(2) + ' s');
}

function callGame() {
    $.getJSON('/random-paragraph') // get random paragraph from server
      .done(para => {
        $('#' + buttonId).hide();
        $('#' + gameContainerId).show();
        setupGame(gameId, resultId, timerId, para.body, para.paragraph_id); // setup game
      })
      .fail((status, error) => {
        console.error('Could not load paragraph:', status, error);
        //alert('Sorry, could not load a paragraph.');
        $('#' + buttonId).hide();
        $('#' + gameContainerId).show();
        setupGame(gameId, resultId, timerId, placeholder, -1); // pass placeholder if deosn't work
      });
  }

function setupGame(elementId, resultId, timerId, text, paragraphId) {
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

    startGame(elementId, resultId, timerId, text, paragraphId); // starts game logic
}

function startGame(elementId, resultId, timerId, text, paragraphId) {
    // starts game logic

    let $word = $('#' + elementId).children().eq(0);
    let $letter = $word.children().eq(0);
    let index = 0;
    let wordIndex = 0;
    const maxIndex = text.length-1;
    let mistakes = 0;

    let start = true;
    let startTime = 0;

    let stats = [] // stores statistic objects
    let interval;

    // used for collecting words and characters user never makes mistake on
    let word_list = text.split(' ');
    let char_list = text.split('');
    let word_check = new Array(word_list.length).fill(true);
    let char_check = new Array(char_list.length).fill(true);

    // used for collecting words and characters user makes mistake on
    let wrong_char_dict = {};
    let wrong_word_dict = {};
    
    $('#' + elementId).on('keydown', function (e) {
        const key = e.key;
        if (/^[a-zA-Z .,!?'-]$/.test(key)) {
            if (start) { // start timer on first valid input
                startTime = Date.now();
                start = false;
                interval = setInterval(() => updateTimerDisplay(timerId, startTime), 10); // update timer every 10ms
            }
            if (key === $letter.text()) { // style inputs accordingly with classes
                // correct input
                if ($letter.hasClass('wrong-char')) {
                    $letter.removeClass('wrong-char');
                    mistakes -= 1; // update mistakes
                }
                $letter.addClass('right-char');
            } else {
                // incorrect input
                if ($letter.hasClass('right-char')) {
                    $letter.removeClass('right-char');
                }
                if (!$letter.hasClass('wrong-char')) {
                    mistakes += 1; // update mistakes
                }
                $letter.addClass('wrong-char');
                // update info on mistake
                char_check[index] = false;
                word_check[wordIndex] = false;
                incrementDict(wrong_char_dict, key);
                incrementDict(wrong_word_dict, $word.text());
            }
            if ($letter.next().length === 0) { // signal to move on to next word (no more letters in word)
                if ($word.next().length === 0 && mistakes === 0) { // end of game if no more words and all correct
                    clearInterval(interval);
                    $('#' + elementId).off('keydown') // turn off keydown event
                    // add statistics
                    stats.push(new statistic('total characters', text.length));
                    stats.push(new statistic('total words', text.split(' ').length));
                    // stats.push(new statistic('seconds to complete', ((Date.now() - startTime) / 1000))); not needed
                    stats.push(new statistic('words per minute', Math.round((text.split(' ').length / ((Date.now() - startTime) / 60000)))));
                    // stats.push(new statistic('characters per minute', Math.round((text.length / ((Date.now() - startTime) / 60000))))); not needed
                    stats.push(new statistic('total mistakes', mistakes));
                    // stats.push(new statistic('finished at', new Date().toLocaleTimeString())); not needed
                    stats.push(new statistic('correct characters', getCorrectDicts(char_list, char_check)));
                    stats.push(new statistic('correct words', getCorrectDicts(word_list, word_check)));
                    stats.push(new statistic('wrong characters', wrong_char_dict));
                    stats.push(new statistic('wrong words', wrong_word_dict));
                    stats.push(new statistic('paragraph id', paragraphId));
                    readResults(resultId, stats);
                    if (paragraphId !== -1) { 
                        // send data if valid paragraph
                        // don't worry about being logged in or not, if not logged in server doesn't save data automatically
                        sendData(stats);
                    }
                    return;
                }
                else if ($word.next().length != 0) { // not end of game, move to next word
                    console.log("moving on to next word");
                    $word = $word.next();
                    $letter = $word.children().eq(0);
                    wordIndex += 1;
                }
                else if ($word.next().length === 0 && mistakes > 0) { // no more words but not end of game (need to go back and correct words to finish)
                    console.log("no more words but not end of game");
                    index -= 1;
                }
            }
            else {
                $letter = $letter.next(); // move to next letter
            }
            index += 1;
            const progress = Math.round((index / maxIndex) * 100);
            $('#progressBar').val(progress);
            $('#runner').css('left', `calc(${progress}% - 20px)`);
            
        } else if (key === 'Backspace' && index > 0) { // handle backspace
            if (!($word.next().length === 0 && mistakes > 0 && ($letter.hasClass('right-char') || $letter.hasClass('wrong-char')))) { // not at end of text
                $letter = $letter.prev();
                if ($letter.length === 0) {
                    $word = $word.prev();
                    $letter = $word.children().last();
                    wordIndex -= 1;
                }
                index -= 1;
            }
            if ($letter.hasClass('right-char')) { // remove styling for character
                $letter.removeClass('right-char');
            }
            if ($letter.hasClass('wrong-char')) {
                $letter.removeClass('wrong-char');
                mistakes -= 1; // update mistakes
            }
        }
        console.log("index: " + index);
        console.log("wordIndex: " + wordIndex);
        console.log("mistakes: " + mistakes);
        console.log("word: " + $word.text());
        console.log("letter: " + $letter.text());
    });
  }

function readResults(resultId, stats) { // function to display results, dynamically creating HTML list with data in statistics
    const $result = $('#' + resultId).empty(); // reset results
    $result.show();
    const $list = $('<ul></ul>').appendTo($result); // create list
    for (let i = 0; i < stats.length; i++) { // add point for each statistic
        const stat = stats[i];
        $('<li></li>')
            .text(stat.toString())
            .appendTo($list);
    }
    // focus onto result list
    $list[0].scrollIntoView({ 
        behavior: 'smooth',  
        block: 'center'       
      });
    $list[0].focus();

    // add button to link to stats page
    $('#statsLinkWrapper').show();
}

function getCorrectDicts(element_list, element_check) { 
    // helper function to get dictionary of correct elements
    // element_list is a list of elements (words or characters)
    // element_check is a list of booleans indicating if the element was correct
    // returns a dictionary of elements and their correct counts
    // getting an element correct means the user never made a mistake on it
    let element_dict = {};
    for (let i = 0; i < element_list.length; i++) {
        if (element_check[i]) {
            let key = element_list[i].toLowerCase().replace(/[.,!?;:'"()]/g, '').trim(); // remove punctuation and trim whitespace
            if (key in element_dict) {
                element_dict[key] += 1;
            } else {
                element_dict[key] = 1;
            }
        }
    }
    return element_dict;
}

function incrementDict(dict, key) { // helper function to increment dictionary values
    key = key.toLowerCase().replace(/[.,!?;:'"()]/g, '').trim(); // remove punctuation and trim whitespace
    if (key in dict) {
        dict[key] += 1;
    } else {
        dict[key] = 1;
    }
}

function sendData(statistics) { // send data to server
    $.ajax({
        type: 'POST',
        url: '/submit-instance-statistics',
        data: JSON.stringify(statistics),
        contentType: 'application/json',
        success: function(response) {
            console.log('Data sent successfully:', response);
        },
        error: function(error) {
            console.error('Error sending data:', error);
        }
    });
}
 