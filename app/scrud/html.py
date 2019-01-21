from sqlalchemy.inspection import inspect
from app import db

class SetFormInputHTML():
    """
    Parameters
    ----------
    type : str
        any html <input> type - form input field defined by html standard
        textarea - html textarea type
        dropdown - form input field is drop down list (PAB defined type)
        boolean - True/False inline radio buttons
        computed - not in form: value is computed and entered by .py code

    label : str
        input label
    form_type : str
        one from set {"update", "create"} : type of modal to display
    class_ : sqlalchemy class
        form will create/update a record in the table with this classname (i.e. Employee)
    column_name : str
        The model relationship attribute (i.e. company) whose records are displayed in the dropdown list
    record : sqlalchemy query result for one row
        values from one row of database table will be shown as values in form input fields (pre-fill current values in update form)
    validate: HTML validate keyword
        this is not fully implemented
    """

    def __init__(self, label, placeholder, value, type, validate, form_type, class_, record, column_name):
        self.label = label
        self.placeholder = placeholder
        self.value = value
        self.type = type
        self.validate = validate
        self.form_type = form_type
        self.class_ = class_
        self.record = record
        self.column_name = column_name

    def get_dropdown_list(self):
        """Build a list of (value, display_str) tuples for all records in the relationship table (ie Employee.company -- company is the relationship table). These records are displayed in the create/update record form dropdown inputs.

        Parameters
        ----------

        Returns
        -------
        ddl : [(value, display_str)] list of value (id or primary key) and display_str for dropdown lists
            lists all records in relationship table (ie company)
        """
        related_class = getattr(self.class_, self.column_name).property.mapper.class_
        q = db.session.query(related_class).all()
        pk_name = inspect(related_class).primary_key[0].name
        ddl = [(None, f"Select {self.column_name}...")]
        for r in q:
            # ddl.append((r.id, r.__str__()))
            ddl.append((getattr(r, pk_name), r.__str__()))
        return ddl

    def set_dropdown_html(self):
        """ Build the HTML for a form <select> input

        Returns
        -------
        input_html : str
            HTML <select> string to define dropdown menu and options
        """
        html = '<div class="form-group">'
        html += '<label class="control-label col-sm-4"> {} </label>'.format(self.label)
        html += '<div class="col-sm-8">'
        # a dropdown is the same for update or create modal
        ddl = self.get_dropdown_list() # drop down list
        if self.form_type == 'update': # get default value 'selected' for dropdown
            # record.column_name returns a model class in a list
            selected_id = getattr(self.record, self.column_name)[0].id
        else:
            selected_id = None

        # build dropdown <option> items
        ddl_str = ''
        for item in ddl:
            if item[0] == selected_id:
                ddl_str += '<option selected value="{}"> {} </option>'.format(item[0], item[1])
            else:
                ddl_str += '<option value="{}"> {} </option>'.format(item[0], item[1])

        html += '<select class="form-control" id="{col_name}" name="{col_name}" "{validate}">'\
            .format(col_name=self.column_name, validate = self.validate)
        html += ddl_str
        html += """</select>"""
        return html

    def set_radio_html(self):
        html = '<div class="form-group">'
        html += '<label class="control-label col-sm-4"> {} </label>'.format(self.label)
        html += '<div class="col-sm-8">'
        if self.form_type == 'update': # show selected row values in form
            modal_title = 'Update record'
            value = getattr(self.record, self.column_name)
            if value: # True
                html += '<label class="radio-inline"><input type="radio" name="{col_name}" value="True" checked>True</label><label class="radio-inline"><input type="radio" name="{col_name}" value="False">False</label>'.format(col_name=self.column_name)
            else: #False
                html += '<label class="radio-inline"><input type="radio" name="{col_name}" value="True">True</label><label class="radio-inline"><input type="radio" name="{col_name}" value="False" checked>False</label>'.format(col_name=self.column_name)
        else: #create record form, show placeholder instead of value
            modal_title = 'create record'
            if self.placeholder == 'True':
                html += '<label class="radio-inline"><input type="radio" name="{col_name}" value="True" checked>True</label><label class="radio-inline"><input type="radio" name="{col_name}" value="False">False</label>'.format(col_name=self.column_name)
            else:
                html += '<label class="radio-inline"><input type="radio" name="{col_name}" value="True">True</label><label class="radio-inline"><input type="radio" name="{col_name}" value="False" checked >False</label>'.format(col_name=self.column_name)
        return html

    def set_textarea_html(self):
        html = '<div class="form-group">'
        html += '<label class="control-label col-sm-4"> {} </label>'.format(self.label)
        html += '<div class="col-sm-8">'
        if self.form_type == 'update': # show selected row values in form
            modal_title = 'Update record'
            value = getattr(self.record, self.column_name)
            html += '<textarea class="form-control" id="{col_name}" name="{col_name}" rows="4" cols="50" {validate}>{value}</textarea>'.format(col_name=self.column_name, validate=self.validate, value=value)
        else: #create record form, show placeholder instead of value
            modal_title = 'create record'
            html += '<textarea class="form-control" id="{col_name}" name="{col_name}" placeholder="{placeholder}" rows="4" cols="50" {validate}></textarea>'.format(col_name=self.column_name, placeholder=self.placeholder, validate=self.validate)
        return html

    def set_date_html(self):
        """ This will override the native support for calendars in browsers that support HTML5 date pickers like Chrome.  I only use Safari, so overriding meets my needs.
        """
        html = '<div class="form-group">'
        html += '<label class="control-label col-sm-4"> {} </label>'.format(self.label)
        html += '<div class="col-sm-8">'
        if self.form_type == 'update': # show selected row values in form
            modal_title = 'Update record'
            value = getattr(self.record, self.column_name)
        else: #create record form, show placeholder instead of value
            modal_title = 'create record'
            value = self.value
        html += '<div class="input-group date" data-provide="datepicker" data-date-format="yyyy-mm-dd"><input type="text" class="form-control" id={col_name} name={col_name} placeholder={placeholder} value={value} {validate}></div>'.format(col_name=self.column_name, placeholder=self.placeholder, value=value, validate=self.validate)
        return html

    def set_input_html(self):
        """ Other standard html <input> types
        """
        html = '<div class="form-group">'
        html += '<label class="control-label col-sm-4"> {} </label>'.format(self.label)
        html += '<div class="col-sm-8">'
        if self.form_type == 'update': # show selected row values in form
            modal_title = 'Update record'
            value = getattr(self.record, self.column_name)
        else: #create record form, show placeholder instead of value
            modal_title = 'create record'
            value = self.value
        html += '<input class="form-control" id="{col_name}" name="{col_name}" type="{type}" placeholder="{placeholder}" value="{value}" {validate}>'.format(col_name=self.column_name, type=self.type, placeholder=self.placeholder, value=value, validate=self.validate)
        return html


def set_function_icon_html(id, table):
    f_str  = '<div class="function_buttons"><ul class="list-inline">'
    f_str = f_str + '<li class="function_update"><a data-id=' + str(id) + ' data-table=' + table  + '><span>update</span></a></li>'
    f_str = f_str + '<li class="function_delete"><a data-id=' + str(id) + ' data-table=' + table + '><span>Delete</span></a></li>'
    f_str = f_str + '</ul></div>'
    return f_str

def set_table_link_html(database, tablename, link_str, row_id, link_id, key, filter):
    """ build html for a link to a child table
    (i.e. Each Company table row has a link to the Employee table.  That link will query the database for a list of all employees of that company.)

    Parameters
    ----------
    database : str
        name of mysql database with table to display
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
    """
    return '<a id="table_link" data-database={database} data-tablename={tablename} data-row_id={row_id} data-link_id={link_id} data-key={key} data-filter={filter} href="#">{link_str}</a>'.format(database=database, tablename=tablename, link_str=link_str, row_id=row_id, link_id=link_id, key=key, filter=filter)

def set_form_html(class_, record, form_type):
    """ Defines the html form as an html string

    Parameters
    ----------
    class_ : sqlalchemy class
        form will create/update a record in the table with this classname (i.e. Employee)
    record : sqlalchemy query
        values from one row of database table will be shown as values in form input fields (pre-fill current values in update form)
    form_type : str
        'update' or 'create' : type of modal to display

    Returns
    -------
    form_str : str
        string of html code that defines the form modal
    modal_title : str
        title displayed in modal
    """
    if form_type == 'update': # show selected row values in form
        modal_title = 'Update record'
    else:
        modal_title = 'create record'
    form_str = ''
    # make form input for each table column
    for column_name, spec in class_.form_spec.items():
        # build form html for each column
        # set defaults for validate and value in form specification
        if 'validate' not in spec:
            spec['validate'] = ""
        if 'value' not in spec:
            spec['value'] = ""
        if 'placeholder' not in spec:
            spec['placeholder'] = ""

        input_html_builder = SetFormInputHTML(spec['label'], spec['placeholder'], spec['value'], spec['type'], spec['validate'], form_type, class_, record, column_name)
        if spec['type'] == 'dropdown': # this is a dropdown <select> element
            form_str += input_html_builder.set_dropdown_html()
        elif spec['type'] == 'boolean': # True/False inline radio button
            form_str += input_html_builder.set_radio_html()
        elif spec['type'] == 'textarea': # textarea
            form_str += input_html_builder.set_textarea_html()
        elif spec['type'] == 'date' or spec['type'] == 'dateISO':
            form_str += input_html_builder.set_date_html()
        elif spec['type'] == 'computed':
            pass # forms do not have an input for computed columns
        else: # Other standard html <input> types
            form_str += input_html_builder.set_input_html()
        form_str += '</div> </div>'
    return form_str, modal_title
