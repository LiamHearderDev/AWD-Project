
window.onload = () => {
    const pfp_text = document.getElementById("pfp_text");
    const username = document.getElementById("username").innerText;
    if (pfp_text) {
        pfp_text.innerText = username.charAt(0);
    }
}