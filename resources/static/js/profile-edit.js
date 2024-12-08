


(function (window, document) {




// Replace editable with input field
function onEditableEdit (element) {
    let editorType = 'input';
    if (element.getAttribute('editable-tag') != null) {
        editorType = element.getAttribute('editable-tag');
    }
    var input = document.createElement(editorType);
    input.value = element.innerText;
    let elementBackup = element;
    element.replaceWith(input);

    input.focus();
    let save = function () {
        elementBackup.innerText = input.value;
        input.replaceWith(elementBackup);
        console.log('Saving', elementBackup.getAttribute('name'), input.value);
    };
    input.addEventListener('blur', save);
    input.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            if (editorType == 'textarea' && event.shiftKey) {
                // do nothing
            } else {
                save();
            }
        }
        if (event.key === 'Escape') {
            input.replaceWith(elementBackup);
        }
    });
};

function handleEvent(e) {
    if (e.target.classList.contains('editable')) {
        onEditableEdit(e.target);
    }
}

// call on document load
document.addEventListener('click', handleEvent);


}(this, this.document));