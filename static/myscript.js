/*this prevents the forms from sumbiting again when the page is reloaded*/
const cleanUri = window.location.href.split('?')[0];
    window.history.replaceState({}, document.title, cleanUri);

/* When the button is clicked switch between hiding and showing the dropdown content */
function toggleDropdown(dropdownId) {
    document.getElementById(dropdownId).classList.toggle("show");
}