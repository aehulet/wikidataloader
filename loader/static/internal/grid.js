function writeGridData() {
    let xhr = new XMLHttpRequest();
    const dat = [];
    gridApi.forEachNode((rowNode, index) => {
        dat.push(rowNode.data)
    });
    xhr.open("POST", '/write_file', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(dat));
}

function loadColumns() {
    let col_ed = document.getElementById('column_editor');
    col_ed.style.display = 'block';
    for (let elem of header_json) {
        let col_name = elem['field'];
        let input_str = "<input type='text' id='" + col_name + "' value='" + col_name + "'><br>";
        $('#column_editor').append(input_str);
    }
}

function updateColumns() {
    let col_ed = document.getElementById('column_editor');
    col_ed.style.display = 'none';
}

