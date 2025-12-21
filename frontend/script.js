const API = "http://127.0.0.1:5000/api";

function login() {
  fetch(API + "/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      username: u.value,
      password: p.value
    })
  }).then(r => {
    if (r.ok) location.href = "dashboard.html";
    else alert("Login failed");
  });
}

function register() {
  fetch(API + "/register", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      username: u.value,
      password: p.value
    })
  }).then(r => {
    if (r.ok) alert("Registered");
    else alert("User exists");
  });
}
