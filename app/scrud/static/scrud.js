'use strict'

$(document).ready(function(){
    console.log("PAB> " + window.location.pathname);
    var url = window.location.href;     // Returns full URL
    var active_table;
    var my_table; // for DataTable

    $("#create_record_button").hide(); // hide this until a table is selected

    // create record submit button
    $('#create_record_button').click(function(e){
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
        var confirm_delete_flag = delete_alert();

        if (confirm_delete_flag) {
            // send delete record request to server
            var request = $.ajax({
                url:           '/scrud/delete_record',
                cache:        false,
                data:         {'id':id, 'table':active_table},
                dataType:     'json',
                type:         'get'
            });
            request.done(function(json) {
                if (json.result == 'success'){
                    show_message('Successfully deleted record with id = '+id, 'success');
                    get_table(active_table);
                } else {
                    show_message('update record request failed', 'error');
                }
            });
            request.fail(function(jqXHR, textStatus) {
                console.log("PAB> AJAX request failed in update record form");
                show_message('update record request failed: ' + textStatus, 'error');
            });
        }
    });

    // display table from navbar menu
    // displays all rows from database table
    $('.dropdown-menu').click(function() {
        //the click is on the child menu item (event.target)
        //but the click is handled by the parent (this)
        var filter, database
        event.preventDefault();
        get_table(event.target.dataset.tablename, database=event.target.dataset.database, filter='all')
        $('#successAlert').text('In user table portion...').show();
    });

    //display table from table link
    $(document).on('click', '#table_link', function(e){
        /*
        Parameters
        ----------
        database : str
            mysql database with table to display
        tablename : str
            name of mysql table to display
        link_str : str
            link text
        row_id : int
            id of the link's table row
        link_id : int
            if filter = 'fk', this id is not used and is set=0
            if filter = 'pk', this is id of record pointed to by link
        key : str
            if foreign key: name of foreign key column (ie 'company_id')
            if primary key: 'id'
        filter : str
            all :  get all rows of table
            pk : get row given by id
            fk : get row's from child table where the child_table.key == id
        */
        e.preventDefault();
        var database = $(this).data('database')
        var tablename = $(this).data('tablename')
        var row_id = $(this).data('row_id')
        var link_id = $(this).data('link_id')
        var key = $(this).data('key')
        var filter = $(this).data('filter')
        // console.log(`PAB> database = ${database}; tablename = ${tablename};  row_id = ${row_id}; link_id = ${link_id}; key = ${key}; filter = ${filter}`);
        get_table(tablename, database=database, row_id=row_id, link_id=link_id, key=key, filter=filter)
    });

    // get table data from server
    function get_table(table, database=null, row_id=null, link_id=null, key=null, filter='all') {
        $.ajax({
            url:           '/scrud/table_view',
            cache:        false,
            data:         {'database':database,
                           'table':table,
                           'row_id':row_id,
                           'link_id':link_id,
                           'key':key,
                           'filter':filter},
            dataType:     'json',
            type:         'get'
        })
        // The response is passed to the function
        .done(function(json) {
          if (json.result == 'success'){

              // if the dt column has a render function, then convert the render str
              // into its equivalent dt render function.
              // should I be using eval() or is it dangerous in this case?
              var i;
              for (i = 0; i < json.columns.length; i++) {
                  if ("render" in json.columns[i]) {
                      json.columns[i].render = eval(json.columns[i].render)
                  }
              }

              show_table(json);
              active_table = json.table;
          } else {
              show_message('Get table request failed', 'error');
          }
        })
        // status codes are passed to the function
        .fail(function( xhr, status, errorThrown ) {
            alert( "Sorry, there was a problem! There is no table by that name." );
        })
    }

    function show_table(table_definition) {
        // if my_table has a table, then destroy table
        if (my_table !== undefined) {
            my_table.destroy();
            $('#myTable').empty(); // empty in case the columns change
        }

        my_table = $('#myTable').DataTable({
            // destroy: true, // allows recreation of data table if called again
            data: table_definition.data,
            columns: table_definition.columns,
            processing: true,
            stateSave: true,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            oLanguage: {
              oPaginate: {
                sFirst:       " ",
                sPrevious:    " ",
                sNext:        " ",
                sLast:        " ",
              },
              sLengthMenu:    "Records per page: _MENU_",
              sInfo:          "Total of _TOTAL_ records (showing _START_ to _END_)",
              sInfoFiltered:  "(filtered from _MAX_ total records)"
          }
        });

        // Show database name
        $("#database").text("Database : " + table_definition.database);

        // Show table name
        $("#table_name").text("Table : " + table_definition.table);

        // show selected table and hide other tables
        $("#create_record_button").show();
        // $('#table_div').show();
    }

    function update_record(element, create_or_update) {
        // update or create a new record to the db table
        var id;

        if ( create_or_update === 'update'){
            id = $(element).data("id");
        } else {
            id = 'None';
        }

        // get the form as an html string
        var request = $.ajax({
          url:           '/scrud/get_form',
          cache:        false,
          data:         {'id':id, 'table':active_table},
          dataType:     'json',
          type:         'get'
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
                    submit_form(e, id, active_table);
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
    }

    function submit_form(e, id, table){
        // Form submit button
        $('#update_record_form').validate();
        if ($('#update_record_form').valid() == true){
            // send form data to server
            var request   = $.ajax({
                url:          '/scrud/update_db?table='+table+'&id='+id,
                cache:        false,
                data:         $('#update_record_form').serialize(),
                dataType:     'json',
                type:         'POST'
            });
            request.done(function(json){
                if (json.result == 'success'){
                    get_table(table);
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
            });
        } else {
            show_message('Form not validated by jQuery validate.');
            console.log("PAB> Form not validated by jQuery validate.");
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

});
