const inputs = document.querySelectorAll("input");
inputs.forEach(function (input) {
    input.addEventListener("focus", function () {
        const parentElement = input.parentElement.parentElement;
        parentElement.classList.add("box-animation");
    });
    input.addEventListener("blur", function () {
        const parentElement = input.parentElement.parentElement;
        parentElement.classList.remove("box-animation");
    });
});
const buttons = document.querySelectorAll("#multiple-btn button");
const form_container = document.getElementById('form_section')
buttons.forEach((button) => {
    button.addEventListener("click", () => {
        form_container.classList.toggle("left-right");
    });
});