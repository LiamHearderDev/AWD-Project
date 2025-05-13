// AJAXify the friends page: send, accept & reject without reload

document.addEventListener('DOMContentLoaded', () => {
  const requestForm = document.getElementById('friendRequestForm');
  if (requestForm) {
    requestForm.addEventListener('submit', async e => {
      e.preventDefault(); // stop the browser from reloading the page
      const formData = new FormData(requestForm);
      try {
        const res  = await fetch(requestForm.action, {
          method:  'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },// mark this as an AJAX request
          body: formData
        });
        const json = await res.json();

        if (json.success) {
          alert('Request sent!');
          requestForm.reset();  // reset the entire form (clears the input)
        } else {
          alert(json.message || 'Failed to send request.');
        }
      } catch (err) {
        console.error(err);
        alert('Network error.');
      }
    });
  }

  // accept & block logic unchanged
  const pendingList = document.getElementById('incomingRequests');
  if (pendingList) {
    pendingList.addEventListener('click', async e => {
      const btn = e.target;
      if (!btn.classList.contains('accept-btn') &&
          !btn.classList.contains('reject-btn')) {
        return;
      }

      const senderId = btn.dataset.senderId;
      const isAccept = btn.classList.contains('accept-btn');
      const url      = isAccept
        ? `/friends/accept/${senderId}`
        : `/friends/reject/${senderId}`;

      try {
        const response  = await fetch(url, {
          method:  'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const json = await response.json();
        if (response.ok && json.success) {
          const li = btn.closest('li');  //li reflects the fact that it holds an <li> element
          if (li) li.remove();
        } else {
          alert(json.message || 'Action failed.');
        }
      } catch (err) {
        console.error(err);
        alert('Network error.');
      }
    });
  }
});