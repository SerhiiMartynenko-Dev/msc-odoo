odoo.define("web_search_filters_ext/static/src/js/views/action_model.js", function (require) {
"use strict";


const { patch } = require('web.utils');
const ActionModel = require('web/static/src/js/views/action_model.js');


patch(ActionModel, 'web_search_filters_ext', {


    _getFacets()
    {
        const facets = this._super();

        for (const facet of facets)
        {
            if (facet.condition === 'and')
            {
                facet.separator = this.env._t("and")
            }
        }

        return facets;
    },


});


});
