// AJAXify the friends page: send, accept & reject without reload





window.onload = () => {

  // makes so that all future AJAX communications to server add CSRF automatically
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content; // get csrf token from header
  $.ajaxSetup({ headers: { 'X-CSRFToken': csrfToken } });

  // accept & block logic unchanged
  const pendingList = document.getElementById('incomingRequests');
  if (pendingList) {

    // Add an event listener to clicking accept or reject friend request
    pendingList.addEventListener('click', (e) => {


      const btn = e.target;
      if (!btn.classList.contains('accept-btn') &&
          !btn.classList.contains('reject-btn')) {
        return;
      }
      
      // Extract the friend request sender's ID from the button, populated by Jinja
      const sender_id = btn.dataset.senderId;

      // Create the URL we will be sending an AJAX POST request to
      const url = btn.classList.contains('accept-btn') ? '/friends/accept-request' : '/friends/reject-request';

      // Send the request
      $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify({ "sender_id": sender_id }),
        contentType: 'application/json',
        success: function(response) {
            console.log('Friend request handled successfully:', response);
            window.location.reload();
        },
        error: function(error) {
            console.error('An error occurred while handling friend request:', error);
            window.location.reload();
        }
      });

      
    });
  }
}
