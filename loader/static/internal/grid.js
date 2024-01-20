let okToNavigate = true;
let isDirty = false;
let col_editor_loaded = false;

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
    }
}

function cellValueChanged(e) {
    isDirty = true;
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
    //alert(JSON.stringify(dat));
    xhr.open("POST", '/write_file', false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(dat));

}

function loadEditor() {
    //use hydrated columns json
    let editor = document.getElementById('col_editor');
    editor.style.display = 'block';
    if (!col_editor_loaded) {
        //iterate over objects in .columns
        for (let i = 1; i <= num_cols; i++) {
            let colName = 'col' + i.toString();
            let row = meta_json["columns"][colName];
            //console.log(row);
            editor.appendChild(generateEditDiv(colName, row));
            editor.appendChild(document.createElement('br'));

        }
        col_editor_loaded = true;
    }
}

function generateEditDiv(colName, row) {
    let the_div = document.createElement("div");
    the_div.id = colName;
    the_div.className = 'edit-panel';

    let name = document.createElement('div')
    //name.id = 'name_' + colName;
    name.className = 'edit-item';
    //name.type = 'text';
    name.innerText = row['name'];
    let name_lbl = document.createElement('div')
    name_lbl.className = 'edit-item';
    name_lbl.innerText = 'name: '

    let prop = document.createElement('input')
    prop.id = 'property_' + colName;
    prop.className = 'edit-item';
    prop.type = 'text';
    prop.value = row['property'];
    let prop_lbl = document.createElement('div')
    prop_lbl.className = "edit-item";
    prop_lbl.innerText = 'assigned to property: '

    let inst_of = document.createElement('input')
    inst_of.id = 'instance_of_' + colName;
    inst_of.className = 'edit-item';
    inst_of.type = 'text';
    inst_of.value = row['instance_of'];
    let inst_of_lbl = document.createElement('div')
    inst_of_lbl.className = "edit-item";
    inst_of_lbl.innerText = 'instance-of code: '

    let literal = document.createElement('input')
    literal.id = 'literal_' + colName;
    literal.className = 'edit-item';
    literal.type = 'text';
    literal.value = row['literal'];
    let literal_lbl = document.createElement('div')
    literal_lbl.className = "edit-item";
    literal_lbl.innerText = 'literal value: '

    let ignore = document.createElement('input')
    ignore.id = 'ignore_' + colName;
    ignore.className = 'edit-item';
    ignore.type = 'text';
    ignore.value = row['ignore'];
    let ignore_lbl = document.createElement('div')
    ignore_lbl.className = "edit-item";
    ignore_lbl.innerText = 'ignore: '

    the_div.appendChild(name_lbl);
    the_div.appendChild(name);
    the_div.appendChild(prop_lbl);
    the_div.appendChild(prop);
    the_div.appendChild(inst_of_lbl);
    the_div.appendChild(inst_of);
    the_div.appendChild(literal_lbl);
    the_div.appendChild(literal);
    the_div.appendChild(ignore_lbl);
    the_div.appendChild(ignore);

    return the_div;
}
function updateColumns() {
    for (let i = 1; i <= num_cols; i++) {
        let colName = 'col' + i.toString();
        let row = meta_json["columns"][colName];
        //row['name'] = document.getElementById("name_" + colName).value;
        row['property'] = document.getElementById("property_" + colName).value;
        row['instance_of'] = document.getElementById("instance_of_" + colName).value;
        row['literal'] = document.getElementById("literal_" + colName).value;
        row['ignore'] = document.getElementById("ignore_" + colName).value;
    }
    let new_json = JSON.stringify(meta_json, null, 4);
    let xhr = new XMLHttpRequest();
    //post changes to source file in backend
    xhr.open("POST", '/write_metadata', false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(new_json);
    //reload file with new headers
    let f = document.getElementById('load_form');
    f.submit();
}

function addOutputColumns() {
    //Called from the drop-down menu as "Step 1".
    if (outputs['outputs'] === true) {
        alert('Output columns have already been added.')
    } else {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", '/add_outputs', false);
        xhr.setRequestHeader('Content-Type', 'application/text');
        xhr.send("outputs");
        let f = document.getElementById('load_form');
        f.submit();

    }
}

