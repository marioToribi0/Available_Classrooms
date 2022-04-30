let form = document.querySelector("body > main > section > div.login-form > form");
let buttonNavbar = document.querySelector("body > nav > div > button");

let actualDisplay = true;

buttonNavbar.onclick = function(){
    if (actualDisplay){
        form.style.opacity = "0";
        form.style.zIndex = "-10";
    }
    else{
        setTimeout(function(){form.style.opacity = "1";}, 200)
        form.style.zIndex = "10";
    }
    actualDisplay = !actualDisplay;
}