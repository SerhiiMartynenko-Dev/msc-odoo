odoo.define('web_search_filters_ext.FilterMenu', function (require) {
"use strict";


const pyUtils = require('web.py_utils');
const core = require('web.core');
const Dialog = require('web.Dialog');
const FilterMenu = require('web.FilterMenu');
const search_filters = require('web.search_filters');


const _lt = core._lt;


FilterMenu.include({


    /**
     *
     * @override
     */
    init: function (parent, filters, fields)
    {
        const self = this;
        this._super.apply(this, arguments);


        // add reference on filter
        self.items.forEach(function (item)
        {
            // check multilevel
            if (item.inspected && item.inspected.type === 'select')
            {
                self.multi_level = true;
            }
        });
    },


    /**
     *
     * @override
     */
    start: function ()
    {
        this._super.apply(this, arguments);

        this._post_renderMenuItems();
    },


    /**
     *
     * @override
     * @private
     */
    _renderMenuItems: function ()
    {
        this._super.apply(this, arguments);

        this._post_renderMenuItems();
    },


    /**
     *
     * @override
     * @private
     * @param {string} itemId
     */
    _onItemClick: function (event)
    {
        event.preventDefault();
        event.stopPropagation();

        const id = $(event.currentTarget).data('id');
        const item = this.items.find(function (item)
        {
            return item.id === id;
        });

        if (item && item.inspected && (item.inspected.type === 'dialog' || item.inspected.type === 'select'))
        {
            if (item.inspected.type === 'dialog')
            {
                this._toggle_dialog(item);
            }
            else if (item.inspected.type === 'select')
            {
                this._toggle_select(item);
            }
        }
        else
        {
            this._super.apply(this, arguments);
        }
    },




    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------


    _post_renderMenuItems: function ()
    {
        const self = this;
        const defs = [];

        // check 'select'-type filters existing and mark dropdown menu as multi-level
        if (this.multi_level)
        {
            this.$menu.addClass('multi-level');


            _.each(self.$menu.find('.o_menu_item'), function (el)
            {
                const $filter = $(el);
                const filter = _.findWhere(self.items, {id: $filter.data('id')});

                if (filter && filter.inspected && filter.inspected.type === 'select')
                {
                    $filter.addClass('dropdown-submenu');
                    const $submenu = $('<ul>', {'class': 'dropdown-menu'});


                    const field = filter.inspected.field;

                    const _createItem = function (item)
                    {
                        if (field.type == 'many2one' || field.type == 'many2many')
                        {
                            item = [item.id, item.display_name];
                        }

                        const $li = $('<li>', {'class': 'o_filter_select_value'});

                        $('<a>', {'class': 'dropdown-item', 'data-filter-select-value': item[0]})
                            .text(item[1])
                            .click(function (event)
                            {
                                const $target = $(event.target);

                                if (field.type == 'selection')
                                {
                                    self._toggle_select_value(filter, $target.data('filterSelectValue'));
                                }
                                else if (field.type == 'many2one' || field.type == 'many2many')
                                {
                                    self._toggle_select_value(filter, {'id': $target.data('filterSelectValue'), 'display_name': $target.text()});
                                }

                                return false;
                            })
                            .appendTo($li);

                        $li.appendTo($submenu);
                    };

                    if (field.type == 'selection')
                    {
                        _.each(field.selection, _createItem);
                    }
                    else if (field.type == 'many2one' || field.type == 'many2many')
                    {
                        const def = $.Deferred();

                        self._rpc({
                                model: field.relation,
                                method: 'search_read',
                                fields: ['id', 'display_name'],
                                domain: filter.domain && pyUtils.eval('domains', [filter.domain]) || [],
                                context: _.extend({}, field.context || {}, filter.inspected.context),
                            })
                            .then(function (result)
                            {
                                _.each(result || [], _createItem);
                                def.resolve();
                            });

                        defs.push(def);
                    }

                    $submenu.appendTo($filter);
                }
            });
        };


        return $.when(defs);
    },






    _toggle_dialog: function (filter)
    {
        const self = this;


        if (filter.inspected)
        {
            // prepare content
            const $content = $('<ul class="o_search_options filter_dialog_content">');

            this._custom_prop_create(
                $content,
                filter
            ).then(function (prop)
            {
                if (prop)
                {
                    $content.find('.o_or_filter').text(filter.inspected.field.string || filter.inspected.field.name);
                    $content.find('.o_searchview_extended_prop_field').parent().hide();

                    // show dialog with config form
                    Dialog.confirm(self, '', {
                        title: _lt("Apply Filter") + ': ' + (filter.description || filter.inspected.field.string || filter.inspected.field.name),
                        $content: $content,
                        confirm_callback: function ()
                        {
                            self._custom_prop_apply(prop);
                        },
                    });
                }
            });
        }
        else
        {
            Dialog.alert(this, _lt("Invalid 'dialog'-type filter definition!"));
        }
    },


    _toggle_select: function (filter)
    {
        if (!filter.inspected || (filter.inspected.field.type !== 'selection' && filter.inspected.field.type !== 'many2one' && filter.inspected.field.type !== 'many2many'))
        {
            Dialog.alert(this, _lt("Invalid 'select'-type filter definition!"));
        }
    },

    _toggle_select_value: function (filter, value)
    {
        const self = this;


        this._custom_prop_create(
            $('<div>'),
            filter,
            (filter.inspected.field.type == 'many2many' ? 'in' : '='),
        ).then(function (prop)
        {
            if (prop)
            {
                if (filter.inspected.field.type === 'selection')
                {
                    prop.$el.find('.o_searchview_extended_prop_value select').val(value).change();
                }
                else if (filter.inspected.field.type === 'many2one')
                {
                    prop.value.widget._setValue(value);
                }
                else if (filter.inspected.field.type === 'many2many')
                {
                    prop.value.widget._setValue({
                        operation: 'ADD_M2M',
                        ids: value,
                    });
                }


                self._custom_prop_apply(prop);
            }
        });
    },





    _custom_prop_create: function ($parent, filter, selected_option)
    {
        if (filter && filter.inspected)
        {
            selected_option = selected_option || (filter.inspected.context && filter.inspected.context.operator);

            const prop = new search_filters.ExtendedSearchProposition(this, filter.inspected.fields, filter);

            if ($parent)
            {
                return prop.appendTo($parent).then(function ()
                {
                    if (selected_option)
                    {
                        prop.$el.find('.o_searchview_extended_prop_op')
                            .val(selected_option).change();
                    }

                    return Promise.resolve(prop);
                });
            }
        }

        return Promise.resolve();
    },

    _custom_prop_apply: function (prop)
    {
        this.propositions = [prop];
        this._commitSearch();
        this._toggleCustomFilterMenu();

        // hide filters menu
        const $btn = this.$el.find('.o_dropdown_toggler_btn');
        if ($btn.attr('aria-expanded'))
        {
            $btn.click();
        }
    },

});


});
