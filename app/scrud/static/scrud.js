'use strict'

function update_record(element, create_or_update) {
    // update or create a new record to the db table
    var id;
    var uid = $(element).data("uid");
    if ( create_or_update === 'update'){
        id = $(element).data("id");
    } else {
        id = 'None';
    }

    // get the form as an html string
    var request = $.ajax({
      url:           '/scrud/get_form',
      cache:        false,
      data:         JSON.stringify({
                      'id':id,
                      'uid':uid
                    }),
      dataType:     'json',
      contentType: 'application/json; charset=utf-8', //data sent to server
      type:         'post'
    });
    request.done(function(json) {
        if (json.result == 'success'){
            // When the user clicks the update record button, open the modal
            // and build the <inputs> for the submit form
            display_form(json.form_html, json.modal_title);
            $('#update_record_form').validate();
            $('#modalSubmit').click(function(e){
                e.preventDefault();
                $('#my_modal').modal('hide');
                submit_form(e, id, uid);
            });
        } else {
            show_message('update record request failed', 'error');
        }
    });
    request.fail(function(jqXHR, textStatus) {
        console.log("PAB> AJAX request failed in update record form");
        show_message('update record request failed: ' + textStatus, 'error');
    });
}

function delete_alert() {
    var confirm_flag;
    if (confirm("Select OK to delete")) {
        confirm_flag = true;
    } else {
        confirm_flag = false;
    }
    return confirm_flag;
}

function display_form(form_html, modal_title) {
    $("#my_modal").modal();
    $('#modal_title').html(modal_title);
    $("#myForm").html(form_html);
    // I tried a number of things to get datepicker to autoclose but
    // couldn't get it to work in a bootstrap modal.  Works fine in
    // a regular html form.

    // hide datepicker after date is selected
    // autohide:true does not work inside of modal for an unknown reason
    $('#mydatepicker').datepicker({
        autoclose:true
    })
    .on('change', function(){
        $('.datepicker').hide();
    });
}

function submit_form(e, id, uid){
    // id : row id
    // uid : table id

    // Form submit button
    $('#update_record_form').validate();
    if ($('#update_record_form').valid() == true){
        // send form data to server
        var request   = $.ajax({
            url: '/scrud/update_db?uid='+uid+'&id='+id,
            // url: '/scrud/update_db',
            cache: false,
            data: $('#update_record_form').serialize(),
            dataType: 'json', // data type returned from server
            type: 'post'
        });
        request.done(function(json){
            if (json.result == 'success'){
                show_message('Success: '+json.message)
            } else {
                //hide_loading_message();
                show_message('create request failed with message '+ json.message, 'error');
            }
        });
        request.fail(function(jqXHR, textStatus){
            //hide_loading_message();
            show_message('create request failed: ' + textStatus, 'error' );
        });
        request.always(function(){
            $('#modalSubmit').off('click'); //prevents multiple ajax calls from going out

            // reload table with latest data
            $("#table"+uid).DataTable().ajax.reload();
        });
    } else {
        show_message('Form not validated by jQuery validate.');
    }
}

// Show message
function show_message(message_text, message_type){
    $('#message').html('<p>' + message_text + '</p>').attr('class', message_type);
    $('#message_container').show();
    if (typeof timeout_message !== 'undefined'){
        window.clearTimeout(timeout_message);
    }
    var timeout_message = setTimeout(function(){
        hide_message();
    }, 8000);
}

// Hide message
function hide_message(){
  $('#message').html('').attr('class', '');
  $('#message_container').hide();
}

function get_datatable(uid, main_table = true) {
    if (main_table) { // main table selected from navbar menu
        var table_element_id = '#table' + uid; //html table element id
    } else { // related table selected from link in main table row
        var table_element_id = '#l_table' + uid; //html table element id
    }

    if ( ! $.fn.DataTable.isDataTable( table_element_id ) ) {
        // initialize table setup and load data
        // Get table initialization specs from views.py
        $.ajax({
            url:"/scrud/init_table",
            type:"post",
            contentType: 'application/json; charset=utf-8', //data sent to server
            dataType:"json",
        })
        .done(function(d) {
            // if d.render has item in list not equal to '', then convert the render str into its equivalent dt render function and add as element to column dict.  I could set render as part of the column spec in controllers.py, but I would still need the eval() here. So rather than doing part in controllers.py and part here, I just add render, where defined, to the column dict here.
            // should I be using eval() or is it dangerous in this case?
            var i;
            for (i = 0; i < d.render.length; i++) {
                if ( d.render[i] != "" ){
                    d.columns[i].render = eval(d.render[i])
                }
            }

            $(table_element_id).DataTable( {
                ajax: {
                    url:"/scrud/get_data",
                    type:"post",
                    data: function(d1) {
                        return JSON.stringify(d1)
                    },
                    dataType:"json", // data type returned from server
                    contentType: 'application/json; charset=utf-8', //data sent to server
                    dataSrc: function(json) {
                        // can modify json returned from server here if needed
                        return json.data; // json formatted for datatables
                    } //dataSrc function
                }, //interior ajax()
                columns: d.columns,
                order: d.order,
                render: d.render
            } ); //DataTable
        }) //.done
    } else {
        // table is already initialized, so just load data
        $(table_element_id).DataTable().ajax.reload();
    }
}

function hide_tables(){
    // Hide all table containers in both main and linked tabs
    $('.my_table_container').hide();
    $('.my_l_table_container').hide();
}

$(document).ready(function(){
    // Hide all table containers in both main and linked tabs
    hide_tables()

    // display table selected from navbar dropdown menu
    $('.dropdown-menu').click(function() {
        event.preventDefault();

        // Hide all table containers
        hide_tables()

        // Show database name
        $("#database").text("Database : " + event.target.dataset.database);

        // Show table name
        $("#table_name").text("Table : " + event.target.dataset.tablename);

        // Get table specs, init table if it doesn't exist, then get table data
        var p_uid = event.target.dataset.uid; // unique id of table (see Tables in views.py)
        var container_id = '#container' + p_uid; // html container element id
        // row_id, fk_id, and fk are not used when table is selected from navbar menu.  They are used when a table is selected from a row link.
        $.ajax({
            url:"/scrud/set_link_ids",
            type:"post",
            contentType: 'application/json; charset=utf-8', //data sent to server
            data: JSON.stringify({ // data to server
                p_uid : p_uid,
                row_id : null,
                fk_id : null,
                fk : null
            })
        })
        .done(function() {
            var main_table;
            get_datatable(p_uid, main_table=true);
        });
        $(container_id).show();
        $('a[href="#main_tab"]').tab('show');
    });

    //display table from table link
    $(document).on('click', '#table_link', function(e){
        /*
        Parameters
        ----------
        p_uid : int
            unique id of requester (parent) table
        c_uid : int
            unique id of requestee (child) table
        row_id : int
            id of the table row that contains the clicked link (parent table)
        fk_id : int
            primary key id of requested row from related table
            If fk_id = None, then this link is to the many side of the relationship and fk != None.
        fk : str
            Name of column with foreign key for related table
            If fk = None, then this link is to the one side of the relationship and fk_id != None.
        */

        e.preventDefault();
        // Hide all table containers
        $('.my_l_table_container').hide();
        var p_uid = $(this).data('uid'); //parent table uid
        var row_id = $(this).data('row_id'); //parent table row
        var fk_id = $(this).data('fk_id'); //child table row id
        var fk = $(this).data('fk'); //parent table fk attr
        $.ajax({
            url:"/scrud/set_link_ids",
            type:"post",
            contentType: 'application/json; charset=utf-8', //data sent to server
            data: JSON.stringify({ // data to server
                p_uid : p_uid,
                row_id : row_id,
                fk_id : fk_id,
                fk : fk
            }),
            dataType:"json", // data type returned from server
        })
        .done(function(json) {
            var main_table;
            var c_uid = json.c_uid;
            get_datatable(c_uid, main_table=false);
            //show table container
            $('#l_container' + c_uid).show();
            $('a[href="#linked_tab"]').tab('show');
        });
    });

    // create record submit button
    $('.create_record_button').click(function(e){
        e.preventDefault();
        update_record(this, 'create');
    });

    // update record button
    $(document).on('click', '.function_update a', function(e) {
      e.preventDefault();
      // Get company information from database
      // get_record_form uses 'this' to determine if create or update button
      // was clicked
      update_record(this, 'update');
    });

    // Cancel modal form
    // The .off() function deregisters the ajax call
    // without this, two ajax calls would go out in sequence if
    // I canceled the modal and then created another record.
    $("#my_modal_cancel").click(function(){
        $('#modalSubmit').off('click');
    });

    // Delete record button
    $(document).on('click', '.function_delete a', function(e) {
        e.preventDefault();
        var id = $(this).data("id");
        var uid = $(this).data("uid");
        var confirm_delete_flag = delete_alert();

        if (confirm_delete_flag) {
            // send delete record request to server
            var request = $.ajax({
                url:           '/scrud/delete_record',
                cache:        false,
                data:         {'id':id, 'uid':uid},
                dataType:     'json', // data type returned from server
                type:         'get'
            });
            request.done(function(json) {
                if (json.result == 'success'){
                    show_message('Successfully deleted record with id = '+id, 'success');
                } else {
                    show_message('update record request failed', 'error');
                }
            });
            request.fail(function(jqXHR, textStatus) {
                console.log("PAB> AJAX request failed in update record form");
                show_message('update record request failed: ' + textStatus, 'error');
            });
            request.always(function(){
                // reload table with latest data
                $("#table"+uid).DataTable().ajax.reload();
            });
        }
    });
})
