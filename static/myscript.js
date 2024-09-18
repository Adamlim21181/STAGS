/* This prevents the forms from submitting again when the page is reloaded
   by removing the query parameters from the URL. This avoids duplicate
   form submissions if the user refreshes the page. */
   const cleanUri = window.location.href.split('?')[0];
   window.history.replaceState({}, document.title, cleanUri);

// Add an event listener to the form's submit event
document.getElementById('delete').addEventListener('submit', 
   function() {location.reload();});


 




   