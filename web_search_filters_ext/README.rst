======================
Web Search Filters Ext
======================

This module provides extra functionality for search filters (search view).


Features
========

* Add extra operators 'is', 'is not', 'in' and 'not in' in custom filters for
  many2one fields (with possibility of select concrete value using standard
  many2one widget)

* Add extra operators 'in' and 'not in' in custom filters for many2many fields
  (with possibility of select concrete value using standard many2many_tags
  widget)

* Possibility definition of filter for concrete field with setup operator and
  value like add custom filter but in separate dialog (see usage example)

* Possibility of usage predefined filters for selection (operator 'is', by
  default) and many2one (operator 'is', by default) fields with select value
  as separate dropdown submenu

* Replace 'OR' condition in search fields by 'AND' condition


Installation
============

Configuration
=============

Usage
=====

Usage of 'dialog' filter type
-----------------------------

For use configuration of filter for some field in separate dialog, you need to
define a special filter in search view with value 'dialog' in attribute 'type'
(all other attributes may be used as usually; you may omit 'string' attribute
value - the string value from field definition will be used then), for example::

<filter name="lang_id" type="dialog" string="Lang Dialog" />

This example add filter in menu with title 'Lang Dialog', but on click it shows
dialog with fields for select appropriate operator for this field type and
field for enter concrete value (for selected operator), exactly like add custom
filter.

Note, in this case name of field defined as value of attribute. If you need to
define this filter type with other name (different like field name), you should
put a special parameters by using context attribute. Next example of filter are
totally equals::

<filter name="lang_id" type="dialog" string="Lang Dialog" />
<filter name="lang_id_2" type="dialog" string="Lang Dialog 2" context="{'field': 'lang_id'}" />
<filter name="lang_id_3" type="dialog" string="Lang Dialog 3" context="{'field_name': 'lang_id'}" />

For define operator, selected by default, you may put parameter 'operator' into
context (in this case, internal operator name must be used, like '=', '!=', 'is',
'is not', 'in', 'not in', 'between' etc.)::

<filter name="lang_id" type="dialog" string="Lang Dialog" context="{'operator': 'not in'}" />


Usage of 'select' filter type
-----------------------------

For select value of filter as separate dropdown submenu, you need to define a
special filter in search view with value 'select' in attribute 'type'
(all other attributes may be used as usually; you may omit 'string' attribute
value - the string value from field definition will be used then), for example::

<filter name="select" type="select" string="Select" />

This example add filter in menu with title 'Select', but on hover it shows
dropdown submenu with all available values for select.

This filter type works for 'selection', 'many2one' and 'many2many' fields type only!
But we do not recommend using this filter for 'many2one'-type fields which may have
a lot of values (for usability purpose).

Note, in this case name of field defined as value of attribute. If you need to
define this filter type with other name (different like field name), you should
put a special parameters by using context attribute. Next example of filter are
totally equals::

<filter name="select" type="select" string="Select" />
<filter name="select_2" type="select" string="Select 2" context="{'field': 'select'}" />
<filter name="select_3" type="select" string="Select 3" context="{'field_name': 'select'}" />

By default, operator 'is' used. But you can define another operator, by put
parameter 'operator' into context (in this case, internal operator name must
be used, like '=', '!=', 'is', 'is not', 'in', 'not in' etc.)::

<filter name="select" type="select" string="Select" context="{'operator': 'not in'}" />

For select all available values for 'many2one'-type field a separate request
used. On make this call, context of filter user. So, next example demonstrate
how to show all available values for 'lang' with inactive also::

<filter name="lang_id" type="select" string="Lang" context="{'active_test': False}" />


Replace 'OR' condition for search field
---------------------------------------

For replace 'OR' condition for some search field values, just add condition
type definition in context of search field. For example::

<field name="lang_ids" context="{'condition': 'and'}" />



Known issues / Roadmap
======================

Bug Tracker
===========

Credits
=======

