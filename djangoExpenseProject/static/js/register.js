const usernameField = document.querySelector("#usernameField");
const emailField = document.querySelector("#emailField");
const passwordField = document.querySelector("#passwordField");

const usernameFeedbackArea = document.querySelector(".username_feedback");
const emailFeedbackArea = document.querySelector(".email_feedback");
const passwordFeedbackArea = document.querySelector(".password_feedback");

const usernameSuccessOutput = document.querySelector(".username_success_output");
const emailSuccessOutput = document.querySelector(".email_success_output");
const passwordSuccessOutput = document.querySelector(".password_success_output");

const showPasswordToggle = document.querySelector(".show_password_toggle");

//username validation
usernameField.addEventListener("keyup",(e)=>{
    const usernameValue = e.target.value;
    usernameSuccessOutput.style.display = "block";
    usernameSuccessOutput.textContent = `Checking ${usernameValue}`
    if(usernameValue.length > 0){
        fetch("/authentication/validate-username", {
            body: JSON.stringify({ username: usernameValue}),
            method: "POST",
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("data", data);
                usernameSuccessOutput.style.display = "none";
                if(data.username_error){
                    usernameField.classList.add("is-invalid");
                    usernameFeedbackArea.style.display="block";
                    usernameFeedbackArea.innerHTML = `<p>${data.username_error} </p>`;
                }else{
                    usernameField.classList.remove("is-invalid");
                    usernameFeedbackArea.style.display="none";
                    usernameFeedbackArea.innerHTML = `<p>${data.username_error} </p>`;
                }
            }
            )
    }
})

//email validation
emailField.addEventListener("keyup",(e)=>{
    const emailValue = e.target.value;
    emailSuccessOutput.style.display = "block";
    emailSuccessOutput.textContent = `Checking ${emailValue}`
    if(emailValue.length > 0){
        fetch("/authentication/validate-email", {
            body: JSON.stringify({ email: emailValue}),
            method: "POST",
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("data", data);
                emailSuccessOutput.style.display = "none";

                if(data.email_error){
                    emailField.classList.add("is-invalid");
                    emailFeedbackArea.style.display="block";
                    emailFeedbackArea.innerHTML = `<p>${data.email_error} </p>`;
                }else{
                    usernameField.classList.remove("is-invalid");
                    emailFeedbackArea.style.display="none";
                    emailFeedbackArea.innerHTML = `<p>${data.email_error} </p>`;
                }
            }
            )
    }
})

// password

const handleToggleInput = (e) => {
    if(showPasswordToggle.textContent === "SHOW"){
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    }else{
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");
    }
}

showPasswordToggle.addEventListener("click",handleToggleInput)