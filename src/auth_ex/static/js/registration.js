var strength = {
  0: "Worst",
  1: "Bad",
  2: "Weak",
  3: "Good",
  4: "Strong",
}

var password1 = document.getElementById('id_password1');
var password2 = document.getElementById('id_password2');
var meter = document.getElementById('password-strength-meter');
var text = document.getElementById('password-strength-text');
var submit = document.getElementById('submit-form');
var score;

password1.addEventListener('input', function() {
  let val = password1.value;
  score = zxcvbn(val).score;

  if (val.length < 10) {
    score = 0;
  }

  meter.value = score;

  if (val !== "") {
    text.innerHTML = "Strength: " + "<strong>" + strength[score] + "</strong>"; 
  } else {
    text.innerHTML = "";
  }
});

password2.addEventListener('input', function() {
  let password = password1.value;
  let confirmation = password2.value;

  if (password === confirmation && score >= 3) {
    submit.disabled = false;
  }
  else {
    submit.disabled = true;
  }
});