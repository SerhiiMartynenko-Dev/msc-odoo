odoo.define('web_search_filters_ext.search_filters', function (require) {
"use strict";


const pyUtils = require('web.py_utils');
const core = require('web.core');
const Widget = require('web.Widget');
const search_filters = require('web.search_filters');
const relational_fields = require('web.relational_fields');
const search_filters_registry = require('web.search_filters_registry');


const _lt = core._lt;


search_filters.ExtendedSearchProposition.include({

    //
    // Inherit base for one2many fields implementation
    //

    init: function (parent, fields, filter)
    {
        this._super.apply(this, arguments);

        this.filter = filter;
        if (_.some(this.fields, function (field) { return field.type === 'one2many'; }))
        {
            this.o2m_fields = {};
            this.o2m_selected = null;
        }
    },


    start: function ()
    {
        const self = this;

        return $.when(this._super.apply(this, arguments)).then(function ()
        {
            if (self.o2m_fields !== undefined)
            {
                $('<select>', {class: "o_input o_searchview_extended_prop_o2m"})
                    .insertBefore(self.$el.find('select.o_searchview_extended_prop_op'));

                self.$o2m = self.$el.find('select.o_searchview_extended_prop_o2m');

                self.$o2m.on('change', function ()
                {
                    const nval = self.$o2m.val();

                    if(self.o2m_selected === null || self.o2m_selected === undefined || nval != self.o2m_selected.name)
                    {
                        self.o2m_select_field(_.detect(self.o2m_fields[self.attrs.selected.name], function (x) { return x.name == nval; }));
                    }
                });
            }
        });
    },


    /**
     *
     * @override
     */
    select_field: function (field, o2m_field)
    {
        if (field.type === 'one2many')
        {
            const self = this;

            if (self.attrs.selected !== null && self.attrs.selected !== undefined)
            {
                self.value.destroy();
                self.value = null;
                self.$el.find('select.o_searchview_extended_prop_op').hide().html('');
            }

            self.attrs.selected = field;
            if(field === null || field === undefined)
            {
                return;
            }

            const fields = self.o2m_fields[field.name];
            if (!fields)
            {
                self._rpc({
                    model: field.relation,
                    method: 'fields_get',
                })
                .then(function (fields)
                {
                    fields = _(fields).chain()
                        .map(function (val, key) { return _.extend({}, val, {'name': key}); })
                        .filter(function (fld) { return !fld.deprecated && fld.searchable && fld.name != field.relation_field && fld.type != 'one2many'; })
                        .sortBy(function (fld) { return fld.string; })
                        .value();

                    self.o2m_fields[field.name] = fields;

                    self._update_o2m_fields(fields);
                });
            }
            else
            {
                self._update_o2m_fields(fields);
            }
        }
        else
        {
            this.$el.find('select.o_searchview_extended_prop_op').show();
            if (!o2m_field && this.$o2m)
            {
                this.$o2m.hide().html('');
                this.o2m_selected = null;
            }

            if (this.attrs.selected)
            {
                // setup fake widget for destroy
                this.value = new Widget(self);
            }
            this._super.apply(this, arguments);
            this.attrs.selected = o2m_field || this.attrs.selected;   // restore
        }
    },


    _update_o2m_fields: function (fields)
    {
        const self = this;


        self.$o2m.html('');

        _.each(fields, function (field)
        {
            $('<option>', {value: field.name})
                .text(String(field.string))
                .appendTo(self.$o2m);
        });

        self.$o2m.css({display: 'block'});
        self.$o2m.change();
    },


    o2m_select_field: function (o2m_field)
    {
        this.o2m_selected = o2m_field;

        this.$el.find('select.o_searchview_extended_prop_op').show();

        this.select_field(o2m_field, this.attrs.selected);

    },


    get_filter: function ()
    {
        const self = this;


        const result = this._super.apply(this, arguments);

        if (result && this.o2m_selected)
        {
            result.attrs.domain = _.map(result.attrs.domain, function (el)
            {
                if (_.isArray(el) && el[0] === self.attrs.selected.name)
                {
                    el[0] = self.attrs.selected.name + '.' + self.o2m_selected.name;
                }

                return el;
            });
            result.attrs.string = result.attrs.string.replace(this.attrs.selected.string + ' ', this.attrs.selected.string + ' -> ' + this.o2m_selected.string + ' ');
        }

        return result;
    },

});


const FilterFieldMany2OneStub = relational_fields.FieldMany2One.extend({


    init: function (parent)
    {
        const self = this;
        this.filter = parent.getParent() && parent.getParent().filter;

        const fieldName = parent.field.name;
        const field = _.extend(parent.field, {
            'type': 'many2one',
        });
        const fieldsInfo = {};
        fieldsInfo[fieldName] = field;

        this.record = {
            model: field.relation,
            fields: fieldsInfo,
            fieldsInfo: {
                'default': fieldsInfo
            },
            data: {},
            getContext: function () {
                return self.filter && self.filter.inspected && self.filter.inspected.context || {};
            },
            getDomain: function () {
                return self.filter && self.filter.domain && pyUtils.eval('domains', [self.filter.domain]) || [];
            }
        };

        const options = {
            mode: 'edit',
            attrs: {
                options: {
                    no_create_edit: true,
                    no_open: true,
                }
            }
        };

        this._super.apply(this, [parent, fieldName, this.record, options]);
    },


    /**
     *
     * @override
     * @param value
     * @param options
     * @private
     */
    _setValue: function (value, options)
    {
        if (value)
        {
            this.value = value.id;
            this.m2o_value = value.display_name;
        }
        else
        {
            this.value = undefined;
            this.m2o_value = '';
        }
        this.str_value = this.m2o_value;

        this._render();
    },


});


const FilterFieldMany2ManyTagsStub = relational_fields.FieldMany2ManyTags.extend({


    init: function (parent)
    {
        const self = this;
        this.filter = parent.getParent() && parent.getParent().filter;

        const fieldName = parent.field.name;
        const field = _.extend(parent.field, {
            'type': 'many2one',
        });
        const fieldsInfo = {};
        fieldsInfo[fieldName] = field;

        this.record = {
            model: field.relation,
            fields: fieldsInfo,
            fieldsInfo: {
                'default': fieldsInfo
            },
            data: {},
            getContext: function () {
                return self.filter && self.filter.inspected && self.filter.inspected.context || {};
            },
            getDomain: function () {
                return self.filter && self.filter.domain && pyUtils.eval('domains', [self.filter.domain]) || [];
            }
        };

        const options = {
            mode: 'edit',
            attrs: {
                options: {
                    no_create_edit: true,
                    no_open: true,
                }
            }
        };

        this._super.apply(this, [parent, fieldName, this.record, options]);

        // set blank initial value
        this._setEmptyValue();
    },


    /**
     *
     * @override
     * @returns {*}
     * @private
     */
    _renderEdit: function ()
    {
        const result = this._super.apply(this, arguments);

        // prevent creation
        this.many2one.can_create = false;
        this.many2one.nodeOptions.no_create = true;
        this.many2one.nodeOptions.no_create_edit = true;

        return result;
    },


    /**
     *
     * @override
     * @param value
     * @param options
     * @private
     */
    _setValue: function (value, options)
    {
        const self = this;


        this.str_value = '';
        if (value && value.operation)
        {
            if (value.operation == 'ADD_M2M')
            {
                const record = value.ids;
                if (!_.contains(this.value.res_ids, record.id))
                {
                    // emulate dataPoint structure
                    record.res_id = record.id;
                    record.data = record;

                    // append value
                    this.value.data.push(record);
                    this.value.res_ids.push(record.id);
                    this.value.count += 1;
                }
            }
            else if (value.operation == 'FORGET')
            {
                const res_id = value.ids[0];
                if (_.contains(this.value.res_ids, res_id))
                {
                    this.value.data = _.reject(this.value.data, function(record){ return record.id === res_id; });
                    this.value.res_ids = _.reject(this.value.res_ids, function(id){ return id === res_id; });
                    this.value.count -= 1;
                }
            }

            _.each(this.value.data, function (el)
            {
                if (self.str_value)
                {
                    self.str_value += ', ';
                }
                self.str_value += '"' + el.display_name + '"';
            });
            self.str_value = '[' + self.str_value + ']';
        }
        else
        {
            this._setEmptyValue();
        }

        this._render();
    },


    _setEmptyValue: function()
    {
        this.value = {
            count: 0,
            res_ids: [],
            data: [],
        };
        this.str_value = '[]';
    },


    /**
     *
     * @override
     * @param event
     * @private
     */
    _onDeleteTag: function (event)
    {
        event.preventDefault();
        event.stopImmediatePropagation();

        this._super.apply(this, arguments);

        return false;
    },

});


const Many2Many = search_filters_registry.get('char').extend({
    tagName: 'span',
    className: 'many2x_filter',
    attributes: {
        type: 'many2many'
    },

    operators: [
        {value: "in", text: _lt("in")},
        {value: "not in", text: _lt("not in")},
        {value: "∃", text: _lt("is set")},
        {value: "∄", text: _lt("is not set")},
    ],

    start: function ()
    {
        return $.when(
            this._super.apply(this, arguments),
            this._create_widget(this._get_default_widget_is_many())
        );
    },

    _get_default_widget_is_many: function()
    {
        return true;
    },

    _create_widget: function (isMany)
    {
        this._destroy_widget();

        this.widget = isMany ? new FilterFieldMany2ManyTagsStub(this) : new FilterFieldMany2OneStub(this);

        return this.widget.appendTo(this.$el);
    },

    _destroy_widget: function ()
    {
        if (this.widget)
        {
            this.widget.destroy();
            this.widget = null;
        }
    },

    show_inputs: function ($operator)
    {
        this._super.apply(this, arguments);

        if ($operator.val() === 'in' || $operator.val() === 'not in')
        {
            this._create_widget(true);
        }
    },

    format_label: function (format, field, operator)
    {
        if (operator.value === 'in' || operator.value === 'not in')
        {
            format = format.replace('"%(value)s"', '%(value)s');
        }

        return this._super.apply(this, [format, field, operator]);
    },

    get_value: function ()
    {
        return (this.widget && this.widget.value) || false;
    },

    get_domain: function (field, operator)
    {
        switch (operator.value)
        {
            case 'in':
                return [[field.name, 'in', this.widget.value.res_ids]];
            case 'not in':
                return [[field.name, 'not in', this.widget.value.res_ids]];

            default:
                return this._super.apply(this, arguments);
        }
    },

    toString: function ()
    {
        return (this.widget && this.widget.str_value) || '';
    },

    destroy: function ()
    {
        this._super.apply(this, arguments);

        this._destroy_widget();
    },
});


const Many2One = Many2Many.extend({
    attributes: {
        type: 'many2one'
    },

    operators: [
        {value: "=", text: _lt("is")},
        {value: "!=", text: _lt("is not")},
        {value: "in", text: _lt("in")},
        {value: "not in", text: _lt("not in")},
        {value: "∃", text: _lt("is set")},
        {value: "∄", text: _lt("is not set")},
    ],

    _get_default_widget_is_many: function()
    {
        return false;
    },

    show_inputs: function ($operator)
    {
        this._super.apply(this, arguments);

        if ($operator.val() === '=' || $operator.val() === '!=')
        {
            this._create_widget(false);
        }
    },
});


search_filters_registry.add('many2many', Many2Many);
search_filters_registry.add('many2one', Many2One);


return {
    FilterFieldMany2OneStub: FilterFieldMany2OneStub,
    FilterFieldMany2ManyTagsStub: FilterFieldMany2ManyTagsStub,

    Many2Many: Many2Many,
    Many2One: Many2One,
}


});
