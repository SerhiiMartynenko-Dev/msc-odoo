/* eslint-env es2021 */
/* eslint-disable max-len,no-shadow */
odoo.define('kw_checkbox_pos.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const models = require('point_of_sale.models');

    models.load_fields('pos.order', 'checkbox_check_ids');
    models.load_fields('pos.order', 'checkbox_check');
    models.load_fields('pos.order', 'checkbox_qr');
    models.load_fields('product.product', 'kw_checkbox_uktzed');
    models.load_fields('product.product', 'kw_checkbox_product_category_id');

    const KwProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _clickProduct (event) {
                var kwOrderLine = this.currentOrder.get_orderlines();
                if (kwOrderLine.length) {
                    if (kwOrderLine[0].product.kw_checkbox_product_category_id[0] ===
                        event.detail.kw_checkbox_product_category_id[0]) {
                        await super._clickProduct(event);
                    } else {
                        await this.showPopup('ErrorPopup', {
                            title : this.env._t('This product has another category and cant be added'),
                            body  : this.env._t('You should make new receipt for this product'),
                        });
                        return;
                    }
                } else {
                    await super._clickProduct(event);
                }
            }
        };
    Registries.Component.extend(ProductScreen, KwProductScreen);

    return ProductScreen;
});
