// AJAXify the friends page: send, accept & reject without reload

document.addEventListener('DOMContentLoaded', () => {
  // Handle username-based friend request separately
  const usernameForm = document.getElementById('friendRequestFormUsername');
  if (usernameForm) {
    usernameForm.addEventListener('submit', async e => {
      e.preventDefault();
      try {
        const response = await fetch(usernameForm.action, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: new FormData(usernameForm),
          credentials: 'same-origin'
        });
        const json = await response.json();
        if (json.success) {
          alert('Friend request by username sent!');
          usernameForm.reset();
        } else {
          alert(json.message || 'Failed to send username request.');
        }
      } catch (err) {
        console.error(err);
        alert('Network error sending username request.');
      }
    });
  }

  // Handle ID-based friend request separately
  const idForm = document.getElementById('friendRequestFormID');
  if (idForm) {
    idForm.addEventListener('submit', async e => {
      e.preventDefault();
      try {
        const response = await fetch(idForm.action, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: new FormData(idForm),
          credentials: 'same-origin'
        });
        const json = await response.json();
        if (json.success) {
          alert('Friend request by ID sent!');
          idForm.reset();
        } else {
          alert(json.message || 'Failed to send ID request.');
        }
      } catch (err) {
        console.error(err);
        alert('Network error sending ID request.');
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
