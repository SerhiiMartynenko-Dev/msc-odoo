/* eslint-env es6 */
/* eslint-disable */
odoo.define('kw_checkbox_pos.models', function (require) {
"use strict";

var models = require('point_of_sale.models');
var web_session = require('web.session');
var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;


models.load_fields('res.company', 'kw_checkbox_salesperson_info');

var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_for_printing: function(){
            var result = _super_order.export_for_printing.apply(this, arguments);
            if (this.pos.company.kw_checkbox_salesperson_info) {
                result.salesperson_info = this.pos.company.kw_checkbox_salesperson_info;
            }
            return result;
        }
    });

var posmodel_super = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
//    Custom server function
    _save_to_server: function (orders, options) {

        for (var i = 0; i < orders.length; i++) {
            var oo = orders[i];
            oo.data.checkbox_check_ids = [];
            oo.data.checkbox_check = '';
            oo.data.checkbox_qr = '';
        }

        if (!orders || !orders.length) {
            return Promise.resolve([]);
        }

        options = options || {};

        var self = this;
        var timeout = typeof options.timeout === 'number' ? options.timeout : 30000 * orders.length;

        var order_ids_to_sync = _.pluck(orders, 'id');

        var args = [_.map(orders, function (order) {
                order.to_invoice = options.to_invoice || false;
                return order;
            })];
        args.push(options.draft || false);
        return this.rpc({
                model: 'pos.order',
                method: 'create_from_ui',
                args: args,
                kwargs: {context: this.session.user_context},
            }, {
                timeout: timeout,
                shadow: !options.to_invoice
            })
            .then(function (server_ids) {
                _.each(order_ids_to_sync, function (order_id) {
                    self.db.remove_order(order_id);
                });
                self.set('failed',false);
                return server_ids;
//            }).catch(function (reason){
//                var error = reason.message;
//                console.warn('Failed to send orders:', orders);
//                if(error.code === 200 ){    // Business Logic Error, not a connection problem
//                    // Hide error if already shown before ...
//                    if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
//                        self.set('failed',error);
//                        throw error;
//                    }
//                }
//                throw error;
            }).then(function (server_ids) {
                for (var ii = 0; ii < orders.length; ii++) {
                    var order = orders[ii];
                    var domain = [['pos_reference', 'like', order.id]];
                    rpc.query({
                        model: 'pos.order',
                        method: 'search_read',
                        args: [domain],
                        context: self.session.user_context,
                    }).then(function (data) {
                        // Result
//                        console.log('this env', this);
//                        console.log('this is data');
//                        console.log(data);
//                        console.log(data[0].checkbox_qr);
//                        console.log(data.length > 0);
//                        console.log(data.length > 0 && data[0].checkbox_qr);
                        if (data.length > 0 && data[0].checkbox_qr) {
                            $('.pos-receipt').append(
                                '<div style="width:100%;display:flex;' +
                                'justify-content: center;"><img style=' +
                                '"width:130px" src="data:image/png;' +
                                'base64,' + data[0].checkbox_qr +
                                '"></div>');
                        }
                    });
                    return server_ids;
                }
            });
    },
});

});
