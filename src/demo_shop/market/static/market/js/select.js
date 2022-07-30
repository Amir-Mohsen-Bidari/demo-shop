document.addEventListener("DOMContentLoaded", selectInputSetup)
function selectInputSetup(event) {
    let selectInputs = document.getElementsByClassName("select-input")
    for (i = 0; i < selectInputs["length"]; i++) {
        if (findParentForm(selectInputs[i])) {
            parentForm = findParentForm(selectInputs[i])
            submits = parentForm.getElementsByClassName("form-btn")
            for (j=0; j<submits["length"]; j++) {
                submits[j].onclick = checkSelectInputs
            }
        }
        selectInputs[i].onclick = toggleOptionList
        selectInputs[i].onblur = collapseOptionList
        selectInputs[i].onkeydown = handleKeys
        select = selectInputs[i].getElementsByTagName("select")[0]
        options = select.getElementsByTagName("option")
        title = selectInputs[i].getElementsByClassName("select-title")[0]
        dropDown = selectInputs[i].getElementsByClassName("select-dropdown")[0]
        selected = dropDown.getElementsByClassName("select-selected")[0]
        selected.textContent = select.selectedOptions[0].textContent
        list = dropDown.getElementsByClassName("select-option-list")[0]
        for (j = 0; j < options["length"]; j++) {
            WGTOption = document.createElement("div")
            WGTOption.setAttribute("value", options[j].value)
            WGTOption.setAttribute("index", j)
            WGTOption.setAttribute("tabindex", "-1")
            WGTOption.setAttribute("class", "select-option")
            WGTOption.textContent =  options[j].textContent
            WGTOption.addEventListener("click", function(event) {
                select = event.target.parentElement.parentElement.parentElement.getElementsByTagName("select")[0]
                selected = event.target.parentElement.parentElement.getElementsByClassName("select-selected")[0]
                select.selectedIndex = event.target.getAttribute("index")
                selected.textContent = event.target.textContent
                event.target.setAttribute("class", "option-selected")
                // event.target.parentElement.parentElement.parentElement.click()
            })
            list.appendChild(WGTOption)
        }
    }
}
function handleKeys(event) {
    optionList = this.getElementsByClassName("select-option-list")[0]
    selected = this.getElementsByClassName("select-selected")[0]
    options = this.getElementsByClassName("select-option")
    select = this.getElementsByTagName("select")[0]
    selectedIndex = select.selectedIndex
    switch (event.code) {
        case "Escape":
        case "Enter":
            this.blur()
            collapseList(optionList)
            break;
        case "ArrowDown":
            if (selectedIndex < options.length-1) {
                select.selectedIndex += 1
                selected.textContent = options[select.selectedIndex].textContent
                options[select.selectedIndex].focus()
                expandList(optionList)
            }
            break;
        case "ArrowUp":
            if (selectedIndex > 0) {
                select.selectedIndex -= 1
                selected.textContent = options[select.selectedIndex].textContent
                options[select.selectedIndex].focus()
                expandList(optionList)
            }
            break;
        default:
            break;
    }
}
function toggleOptionList(event) {
    let optionList = this.getElementsByClassName("select-option-list")[0]
    // let select = this.getElementsByTagName("select")[0]
    if (optionList.style.maxHeight == "15rem") {
        collapseList(optionList)
    } else {
        expandList(optionList)
    }
}
function collapseOptionList(event) {
    let optionList = this.getElementsByClassName("select-option-list")[0]
    collapseList(optionList)
}
function expandList(list) {
    list.style.maxHeight = "15rem"
    list.style.padding = "0.5rem 1rem"
    list.style.opacity = "1"
    list.style.overflowY = "auto"
}
function collapseList(list) {
    list.style.overflowY = "hidden"
    list.style.maxHeight = "0"
    list.style.padding = "0 1rem"
    list.style.opacity = "0"
}

function checkSelectInputs(event) {
    form = findParentForm(event.target)
    selInputs = form.getElementsByClassName("select-input")
    for (i=0; i<selInputs["length"]; i++) {
        select = selInputs[i].getElementsByTagName("select")[0]
        if (!(select.validity.valid)) {
            error = document.createElement("li")
            error.textContent = "انتخاب یک گزینه لازم است"
            errorList =  selInputs[i].nextElementSibling
            if (errorList == null) {
                errorList = document.createElement("ul")
                selInputs[i].parentElement.appendChild(errorList)
            }
            found = false
            for (j=0; j<errorList.childNodes.length; j++) {
                if (errorList.childNodes[j].textContent == error.textContent) {
                    found = true
                    break
                }
            }
            if (!found) {
                errorList.appendChild(error)
            }
            selInputs[i].focus()
        } else if (form.checkValidity()) {
            form.submit()
        }
    }
}
function findParentForm(element) {
    parent = element.parentElement
    if (parent.tagName == 'FORM') {
        return parent
    } else if (parent.tagName == 'BODY') {
        return false
    }
    return findParentForm(parent)
}