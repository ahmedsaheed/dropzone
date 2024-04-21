"use strict";

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyAD3KGLLWHlUkNS5E1H0YGEmnkFrOClyPk",
  authDomain: "griffithlabs-414212.firebaseapp.com",
  projectId: "griffithlabs-414212",
  storageBucket: "griffithlabs-414212.appspot.com",
  messagingSenderId: "303368494173",
  appId: "1:303368494173:web:6623f824cd71d44a7041b4",
};

window.addEventListener("load", function () {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  UpdateUI(document.cookie);
  document.getElementById("sign-up")?.addEventListener("click", () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        console.log(user);
        user.getIdToken().then((token) => {
          document.cookie = `token=${token};path=/;SameSite=Strict`;
          window.location = "/";
        });
      })
      .catch((error) => {
        let errorMessage = humanizeFirebaseLoginError(error);
        let errorElement = document.getElementById("login-error");
        errorElement.innerText = errorMessage;
        errorElement.hidden = false;
        console.log(error.code + " " + error.message);
        console.log(error.code + " " + error.message);
      });
  });

  document.getElementById("login")?.addEventListener("click", () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        console.log(user);
        // force token refresh
        user.getIdToken(true).then((token) => {
          document.cookie = `token=${token};path=/;SameSite=Strict`;
          window.location = "/";
        });
      })
      .catch((error) => {
        let errorMessage = humanizeFirebaseLoginError(error);
        let errorElement = document.getElementById("login-error");
        errorElement.innerText = errorMessage;
        errorElement.hidden = false;
        console.log(error.code + " " + error.message);
      });
  });
  var signOutButtons = document.querySelectorAll("#sign-out");
  signOutButtons.forEach((sob) => {
    sob?.addEventListener("click", () => {
      signOut(auth).then(() => {
        document.cookie = "token=;path=/;SameSite=Strict";
        window.location = "/";
      });
    });
  });
});

function UpdateUI(cookie) {
  var token = parseCookieToken(cookie);
  var loginBox = document.getElementById("login-box");
  if (token.length > 0) {
    if (loginBox) {
      loginBox.style.display = "none";
    }
  } else {
    if (loginBox) {
      loginBox.style.display = "flex";
    }
  }
}

function parseCookieToken(cookie) {
  var strings = cookie.split(";");

  for (var i = 0; i < strings.length; i++) {
    var pair = strings[i].split("=");
    if (pair[0] == "token") {
      return pair[1];
    }
  }
  return "";
}

function humanizeFirebaseLoginError(err) {
  console.log({ err }, err.code);
  switch (err.code) {
    case "auth/email-already-in-use":
      return "Email already in use";
    case "auth/invalid-login-credentials":
      return "Invalid login credentials";
    case "auth/invalid-email":
      return "Invalid email";
    case "auth/weak-password":
      return "Weak password";
    case "auth/user-not-found":
      return "User not found";
    case "auth/wrong-password":
      return "Wrong password";
    default:
      return "Unknown error";
  }
}
