
// In this file is some basic JS form validation. The more advanced validation is done on the server. 
// This is mostly for convenience and avoiding unnecessary requests.

window.onload = () => {

    document.getElementById("login_form").addEventListener('submit', (event) => {
        const username = document.getElementById("login_input_username").value.trim();
        const password = document.getElementById("login_input_password").value.trim();

        // Clears all js_flash messages from the screen.
        clear_js_flash();

        // Check that the username and password are not empty.
        if (!username || !password) {
            js_flash("Username and password cannot be empty.");
            event.preventDefault();
            return;
        }

        // Check for username length
        if (username.length < 3 || username.length > 32) {
            js_flash("Usernames must be between 3-32 characters.");
            event.preventDefault();
            return;
        }

        // Checks password length
        if (password.length < 3 || password.length > 32) {
            js_flash("Passwords must be between 3-32 characters.");
            event.preventDefault();
            return;
        }

        // Checks that usernames have acceptable characters.
        if (!/^[a-zA-Z0-9_]{3,32}$/.test(username)) {
            js_flash("Username must contain only letters, numbers, or underscores.");
            event.preventDefault();
            return;
        }
    });
}


/**
 * This is used only to clear all js_flash messages from the screen.
 */
function clear_js_flash() {
    $("#login_flash_container .js_flash").remove();
}

/**
 * This is a helper function to do essentially Flask's "flash()" function in JS.
 * This function first deletes all previous js_flash messages, then adds the new one.
 * @param {*} message   This is the message that will be displayed.
 */
function js_flash(message) {

    // This gets all previous messages using jQuery and deletes any duplicates of this one.
    $("#login_flash_container .js_flash").filter(function() { return $(this).text() === message; }).remove();
    
    const flash_container = document.getElementById("login_flash_container");
    const new_message = document.createElement("p");
    new_message.classList.add("error_message");
    new_message.classList.add("js_flash");
    new_message.innerText = message;
    flash_container.appendChild(new_message);
}