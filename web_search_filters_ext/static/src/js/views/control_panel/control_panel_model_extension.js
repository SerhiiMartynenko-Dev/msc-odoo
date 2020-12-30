odoo.define('web_search_filters_ext/static/src/js/control_panel/control_panel_model_extension.js', function (require) {
"use strict";


const { patch } = require('web.utils');
const pyUtils = require('web.py_utils');
const Domain = require('web.Domain');
const ControlPanelModelExtension = require('web/static/src/js/control_panel/control_panel_model_extension.js');


patch(ControlPanelModelExtension, 'web_search_filters_ext', {


    _extractAttributes: function (filter, attrs)
    {
        // call super at first
        this._super.apply(this, arguments);


        // then check additional properties
        if (filter.type === 'filter')
        {
            if (attrs.type === 'dialog' || attrs.type === 'select')
            {
                // detect field name
                let fieldName = attrs.name;
                let context = {};

                if (attrs.context)
                {
                    try
                    {
                        context = pyUtils.eval('context', attrs.context);
                        fieldName = context.field || context.field_name || fieldName;
                    }
                    catch (e) {}
                }

                // try to find field by name
                const field = (fieldName && this.fields[fieldName]) || null;

                // create filters map
                if (field)
                {
                    const fields = {};
                    fields[fieldName] = field;

                    filter.inspected = {
                        type: attrs.type,
                        filter: filter,
                        fieldName: fieldName,
                        context: context,
                        field: field,
                        fields: fields,
                    };

                    if (!attrs.string && !attrs.help)
                    {
                        attrs.string = filter.inspected.field.string;
                    }
                }
            }
        }
        else if (filter.type === 'field')
        {
            if (attrs.context)
            {
                try
                {
                    const context = pyUtils.eval('context', attrs.context);

                    if (context.condition)
                    {
                        filter.condition = context.condition.toLowerCase();
                    }
                }
                catch (e) {}
            }
        }
    },



    _getFacets()
    {
        //
        // Full override of super method for add 'condition' in facet descriptor
        //
        const facets = this._getGroups().map(({ activities, type, id }) => {
            const values = this._getFacetDescriptions(activities, type);
            const filter = activities[0].filter
            const title = filter.description;
            const condition = filter.context ? filter.context.condition : undefined;
            return { groupId: id, title, type, values, condition };
        });
        return facets;
    },


    _getAutoCompletionFilterDomain(filter, filterQueryElements)
    {
        // call super ant first
        const result = this._super.apply(this, arguments);

        if (filter.condition === 'and')
        {
            //
            // replace OR with AND
            //
            let domains = _.without(pyUtils.eval('domains', [result]), '|');
            domains = domains.map(function (el) {
                return [el];
            });
            domains = domains.map(Domain.prototype.arrayToString);

            return pyUtils.assembleDomains(domains, filter.condition.toUpperCase());
        }

        return result;
    },


});


});
