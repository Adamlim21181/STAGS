/*this prevents the forms from sumbiting again when the page is reloaded*/
const cleanUri = window.location.href.split('?')[0];
    window.history.replaceState({}, document.title, cleanUri);

/* When the button is clicked switch between hiding and showing the dropdown content */
function alldrp() {
    document.getElementById("allaround").classList.toggle("show");
}

function floordrp() {
  document.getElementById("floor").classList.toggle("show");
}

function pommeldrp() {
  document.getElementById("pommel").classList.toggle("show");
}

function ringsdrp() {
  document.getElementById("rings").classList.toggle("show");
}

function vaultdrp() {
  document.getElementById("vault").classList.toggle("show");
}

function pbarsdrp() {
  document.getElementById("pbars").classList.toggle("show");
}

function highbardrp() {
  document.getElementById("highbar").classList.toggle("show");
}