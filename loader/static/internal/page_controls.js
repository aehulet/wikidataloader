window.addEventListener('mouseup', function (event) {
    if ($(event.target).hasClass('close')) {
        let closers = document.getElementsByClassName('close');
        for (let elem of closers) {
            elem.closest('div').style.display = 'none';
        }

    }
});

function openFileDialog() {
    $('#file_opener').click();
}