const shouldPost = false; // This is a placeholder for when we have a backend to send the data to.


/* This handles the submit button's OnClick event.
This should check if the information being used to login to the website is valid and it should then direct the user to the home page using Flask. */
function handleSubmit(event){
    event.preventDefault();
    const username = document.getElementById("login_input_username").value;
    const password = document.getElementById("login_input_password").value;

    const status = validateLoginInfo(username, password);
    if (status < 0) {
        switch (status) {
            case -1:
                alert("Username and Password must be strings.");
                break;
            case -2:
                alert("Username and Password must not be empty.");
                break;
            case -3:
                alert("Username must be at least 5 characters long.");
                break;
            case -4:
                alert("Password must be at least 8 characters long.");
                break;
            case -5:
                alert("Password must include a special character.");
                break;
            default:
                alert("Unknown error occurred. Please reload the page and try again.");
        }
    }
    else {
        // If the login info is valid, submit the form
        if (shouldPost == true){ // This will be false until we have a backend to send the data to.
            fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            })

            .then((response) => {
                if (response.ok) {
                    // If the response is ok, redirect to the game
                    window.location.href = "/game";
                } else {
                    // If the response is not ok, show an error message
                    alert("Login failed. Please check your username and password.");
                }
            })
        }
        else {
            window.location.href = "/game";
        }
    }
}




/* It checks if a string includes any of the provided substrings.
Could use this to avoid RCE attacks to avoid user data having dangerous special characters.
Returns 0 if true, returns 1 if false.
Returns a negative number if there is an error. */
function includesAny(str, subStrings){
    console.log(subStrings);
    if (typeof str !== 'string') { console.log("NOT A STIRNG"); return -1; }
    if (subStrings.length < 1) { return -1; }
    if (str.length < 1) { return -1; }

    for (let i = 0; i < subStrings.length; i++){
        const subStr = subStrings[i];
        if (str.includes(subStr) == true) { return 0; }
        console.log("Substr: " + subStr + " not found in " + str);
    }
    return 1;
}

/* This does client validation on the provided login info.
Returns non-negative if everything succeeds. 
Returns a negative number if there is an issue.
Each non-negative number corresponds to a specific issue to be solved. */
function validateLoginInfo(username, password){
    
    if (typeof username !== 'string') { return -1; }                // username is not a string
    if (typeof password !== 'string') { return -1; }                // password is not a string

    const specialChars = ["!", "@", "#", "$", "%", "^", "&", "(", ")", "_", "-", "+", "="];

    if (username.length === 0 || password.length === 0) { return -2; } // Password or Username have not been entered

    // TO DO: check for RCE here

    if (username.length < 5) {return -3; }                          // Need longer username
    if (password.length < 8) {return -4; }                          // Need longer password
    if (includesAny(password, specialChars) === 1) { return -5; }   // Need to include a special character

    return 0;
}


// Once the page has loaded, this executes
window.onload = () => {
    document.getElementById("login_form").addEventListener("submit", handleSubmit);
    console.log("yep, its working");
}