let file_open_input = document.getElementById('file_opener');
let menu_button = document.getElementById('menu_btn');
let proc_menu = document.getElementById('process_menu');
let mouse_x, mouse_y;
let columnObjects;
window.onload = function() {

    //columnObjects = JSON.parse(meta_json);

    window.addEventListener('mouseup', function (event) {
        if ($(event.target).hasClass('close')) {
            let closers = document.getElementsByClassName('close');
            for (let elem of closers) {
                elem.closest('div').style.display = 'none';
            }

        }
    });

}

function checkSelect() {
    //Adds csv file to application when user confirms selection.
    let val = document.getElementById('file_opener').value;
    if (val) {
        $('#new_file_form').submit();
    }


}


function openFileDialog() {
    $('#file_opener').click();
}

function hideShowMenu() {
    let button = document.getElementById('menu_btn');
    let menu = document.getElementById('process_menu');
    let the_x, the_y;
    let rect = button.getBoundingClientRect();
    the_x = (Math.trunc(rect.x) - 200).toString();
    the_y = (Math.trunc(rect.y) + 30).toString();
    menu.style.left = the_x + 'px';
    menu.style.top = the_y + 'px';

    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'block';
    }


}