document.addEventListener("DOMContentLoaded", imageInputSetup)
function imageInputSetup(event){
    let fileInputs = document.getElementsByClassName("file-input")
    for (i=0; i < fileInputs["length"]; i++) {
        input = fileInputs[i].getElementsByTagName("input")[0]
        input.addEventListener('change',function (event){
            parent = event.target.parentElement
            fileName = event.target.files[0].name
            preview = parent.getElementsByClassName("file-input-preview")[0]
            text = parent.getElementsByClassName("file-input-text")[0]
            text.textContent = fileName
        })
    }
}