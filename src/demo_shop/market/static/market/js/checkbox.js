document.addEventListener("DOMContentLoaded", checkboxInputSetup)
function checkboxInputSetup(event){
    let checkboxInputs = document.getElementsByClassName("checkbox-input")
    for (i=0; i < checkboxInputs["length"]; i++) {
        input = checkboxInputs[i].getElementsByTagName("input")[0]
        button = checkboxInputs[i].getElementsByClassName("checkbox-input-button")[0]
        box = checkboxInputs[i].getElementsByClassName("checkbox-input-box")[0]
        inactive = checkboxInputs[i].getElementsByClassName("checkbox-inactive")[0]
        active = checkboxInputs[i].getElementsByClassName("checkbox-active")[0]
        if (input.checked){
            inactive.style.opacity = "0"
            active.style.opacity = "1"
            button.style.transform = "translate(-1.5rem,0)"
            box.style.backgroundColor = "var(--color-p4)"
        } else if (!(input.checked)) {
            inactive.style.opacity = "1"
            active.style.opacity = "0"
            button.style.transform = "translate(0,0)"
            box.style.backgroundColor = "var(--color-s4)"
        }
        input.addEventListener('change',function (event){
            parent = event.target.parentElement
            button = parent.getElementsByClassName("checkbox-input-button")[0]
            box = parent.getElementsByClassName("checkbox-input-box")[0]
            inactive = parent.getElementsByClassName("checkbox-inactive")[0]
            active = parent.getElementsByClassName("checkbox-active")[0]
            if (event.target.checked){
                inactive.style.opacity = "0"
                active.style.opacity = "1"
                button.style.transform = "translate(-1.5rem,0)"
                box.style.backgroundColor = "var(--color-p4)"
            } else if (!(event.target.checked)) {
                inactive.style.opacity = "1"
                active.style.opacity = "0"
                button.style.transform = "translate(0,0)"
                box.style.backgroundColor = "var(--color-s4)"
            }
        })
    }
}