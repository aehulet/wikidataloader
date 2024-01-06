let okToNavigate = true;
let isDirty = false;
function manageEdits() {
    let btn = document.getElementById('edit_btn');
    if (btn.innerText === 'Start Editing') {
        btn.innerText = "Stop Editing";
        let first_col = header_json[0]["field"];
        gridApi.setGridOption('suppressClickEdit', false);
        gridApi.setFocusedCell(0, first_col);
        gridApi.startEditingCell({
            rowIndex: 0,
            colKey: first_col,
        });
        okToNavigate = false;
        //console.log('ok: ' + okToNavigate);
    } else {
        btn.innerText = "Start Editing";
        gridApi.stopEditing();
        gridApi.setGridOption('suppressClickEdit', true);
        okToNavigate = true;
        //console.log('ok: ' + okToNavigate);
    }
}

function cellValueChanged(e) {
    //console.log("dirty", e);
    isDirty = true;
    //console.log('dirty: ' + isDirty);
}

function cellEditingStopped(e) {
    //okToNavigate = true;
    //console.log('cell editing stopped');
}

function writeGridData() {
    let xhr = new XMLHttpRequest();
    const dat = [];
    gridApi.forEachNode((rowNode, index) => {
        dat.push(rowNode.data)
    });
    xhr.open("POST", '/write_file', false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(dat));
}

function loadColumns() {
    let col_ed = document.getElementById('column_editor');
    col_ed.style.display = 'block';
    for (let elem of header_json) {
        let col_name = elem['field'];
        let col_check = document.getElementById(col_name);
        if (!col_check) {
            let input_str = "<input type='text' class='txt' id='" + col_name + "' value='" + col_name + "'><br>";
            $('#column_editor').append(input_str);
        }
    }
}

function updateColumns() {
    let col_ed = document.getElementById('column_editor');
    col_ed.style.display = 'none';
    let comma_str = ''
    for (let elem of header_json) {
        let val = document.getElementById(elem['field']).value;
        comma_str += val + ',';
    }
    comma_str = comma_str.slice(0, comma_str.length - 1);
    let xhr = new XMLHttpRequest();
    xhr.open("POST", '/write_header', false);
    xhr.setRequestHeader('Content-Type', 'application/text');
    xhr.send(comma_str);
    let f = document.getElementById('load_form');
    f.submit();

}


