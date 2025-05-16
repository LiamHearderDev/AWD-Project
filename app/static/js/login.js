
// In this file is some basic JS form validation. The more advanced validation is done on the server. 
// This is mostly for convenience and avoiding unnecessary requests.

/**
 * This is a function that checks the validity of user inputs for logging in.
 * This function will also flash an error message to the screen if it detects any issues.
 * @param {*} username      The username that has been entered in the form.
 * @param {*} password      The password that has been entered in the form.
 * @returns {boolean}       `Boolean` -- Returns `true` if the inputs are valid. Returns `false` if the inputs are invalid.
 */
function login_checkInputValidity(username, password) {
    // Check that the username and password are not empty.
    if (!username || !password) {
        js_flash("Username and password cannot be empty.");
        return false;
    }

    // Check for username length
    if (username.length < 3 || username.length > 32) {
        js_flash("Usernames must be between 3-32 characters.");
        return false;
    }

    // Checks password length
    if (password.length < 3 || password.length > 32) {
        js_flash("Passwords must be between 3-32 characters.");
        return false;
    }

    // Checks that usernames have acceptable characters.
    if (!/^[a-zA-Z0-9_]{3,32}$/.test(username)) {
        js_flash("Username must contain only letters, numbers, or underscores.");
        return false;
    }

    return true;
}

/**
 * This is a function that checks the validity of user inputs for registering an account.
 * This function will also flash an error message to the screen if it detects any issues.
 * @param {*} username      The username that has been entered in the form.
 * @param {*} email         The email that has been entered in the form.
 * @param {*} password      The password that has been entered in the form.
 * @param {*} password2     The password confirmation.
 * @returns {boolean}       `Boolean` -- Returns `true` if the inputs are valid. Returns `false` if the inputs are invalid.
 */
function register_checkInputValidity(username, email, password, password2) {

    // Check that no fields are empty.
    if (!username || !password || !email || !password2) {
        js_flash("Please ensure that all fields are filled out.");
        return false;
    }

    // Check for username length
    if (username.length < 3 || username.length > 32) {
        js_flash("Usernames must be between 3-32 characters.");
        return false;
    }

    // Checks password length
    if (password.length < 3 || password.length > 32) {
        js_flash("Passwords must be between 3-32 characters.");
        return false;
    }

    if (password != password2) {
        js_flash("Passwords must match exactly.");
        return false;
    }

    // Checks that usernames have acceptable characters.
    if (!/^[a-zA-Z0-9_]{3,32}$/.test(username)) {
        js_flash("Username must contain only letters, numbers, or underscores.");
        return false;
    }

    return true;
}




window.onload = () => {

    // Perform front-end validation for the login form
    const login_form = document.getElementById("login_form");
    if (login_form) {
        login_form.addEventListener('submit', (event) => {
            const username = document.getElementById("login_input_username").value.trim();
            const password = document.getElementById("login_input_password").value.trim();

            // Clears all js_flash messages from the screen.
            clear_js_flash();
            if (login_checkInputValidity(username, password) === false) { 
                event.preventDefault();
                return;
            }
        });
    }

    // Perform front-end validation for the registry form
    const register_form = document.getElementById("register_form");
    if (register_form) {
        console.log("Yep found the form and did stuff");
        register_form.addEventListener('submit', (event) => {
            const username  = document.getElementById("register_username").value.trim();
            const email     = document.getElementById("register_email").value.trim();
            const password  = document.getElementById("register_password").value.trim();
            const password2 = document.getElementById("register_password2").value.trim();

            // Clears all js_flash messages from the screen.
            clear_js_flash();
            if (register_checkInputValidity(username, email, password, password2) === false) { 
                event.preventDefault();
                return;
            }
        });
    }
    
}


/**
 * This is used only to clear all js_flash messages from the screen.
 */
function clear_js_flash() {
    $("#flash_container .js_flash").remove();
}

/**
 * This is a helper function to do essentially Flask's "flash()" function in JS.
 * This function first deletes all previous js_flash messages, then adds the new one.
 * @param {string} message   This is the message that will be displayed.
 */
function js_flash(message) {
    // This gets all previous messages, using jQuery, find any with a matching message and deletes them.
    $("#flash_container .js_flash").filter(function() { return $(this).text() === message; }).remove();
    
    // Appends a new message to the flash container.
    $("#flash_container").append(`<p class='error_message js_flash'>${message}</p>`);
}