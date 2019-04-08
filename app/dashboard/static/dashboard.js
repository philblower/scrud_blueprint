'use strict'

function get_demo_table(table_element_id) {
    /* Displays a table using DateTables. The table columns and data are
    set up in python with any number of columns, column titles, and any
    number of rows.

    This example uses an ajax call outside of DataTable to get the table column configuration and data.  It destroys the DataTable if a second or more call to the table is made after it is initialized.  It uses destroy because ajax.reload is not available when ajax is called from outside of the DataTable function.

    Parameters
    ----------
    table_element_id : str
        HTML element id (ie '#generic_table_1')

    Notes
    -----
    JSON returned from python should be constructed as shown in this example:
        {
        "data": [
                    {
                        "name": "Tiger Nixon",
                        "position": "System Architect",
                        "salary": "320800.00",
                        etc.
                    },
                    {etc.}
                ],
        "column_config" : [
                            { title: "Name", data: "name" },
                            { title: "Position", data: "position" },
                            { title: "Salary ($)", data: "salary" },
                            etc.
                        ]
        }
    */
    $.ajax({
        url:"/dashboard/get_demo_table",
        type:"get",
        dataType:"json", // data type returned from server
    })
    .done(function(d) {
        $(table_element_id).DataTable( {
            destroy : true, // enable redisplay of table from menu click
            data: d.data,
            columns: d.column_config,
        } ); //DataTable
    })
}

$(document).ready(function() {
    $('#get_demo_table').click(function() {
        get_demo_table("#table_demo");
    });

    // test an autoclose datepicker
    $('.datepicker').datepicker();

    $('#form_demo').on('submit', function(event) {
        var radio = $('input[name = "optradio"]:checked').val();
        $.ajax({
            data : {
                startdate : $('#startdate').val(),
                enddate : $('#enddate').val(),
                radio : radio
            },
            type : 'POST',
            url : '/dashboard/get_demo_form'
        })
        .done(function(data) {
            if (data.error) {
                $('#errorAlert').text(data.error).show();
                $('#successAlert').hide();
            } else {
                $('#successAlert').text(`startdate =${data.startdate}; enddate=${data.enddate}; radio=${data.radio}`).show();
                $('#errorAlert').hide();
            }

            // display table (data is just random data, not linked to form request)
            $(table_demo).DataTable( {
                destroy : true, // enable redisplay of table from menu click
                data: data.data,
                columns: data.column_config,
            } ); //DataTable
        });

        event.preventDefault();
    });
});
