/* eslint-env es6 */
/* eslint-disable */
odoo.define('kw_checkbox_pos.PaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const models = require('point_of_sale.models');
    models.load_fields('pos.payment.method', 'kw_checkbox_product_category_id');
    models.load_fields('pos.payment.method', 'kw_checkbox_is_register_receipt');

    const KwPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            addNewPaymentLine({ detail: paymentMethod }) {
                var kwOrderLine = this.currentOrder.get_orderlines()
                if (kwOrderLine[0].product.kw_checkbox_product_category_id[0] ===
                    paymentMethod.kw_checkbox_product_category_id[0]) {
                    if (!this.paymentLines[0]) {
                        super.addNewPaymentLine(...arguments);
                    } else if (paymentMethod.kw_checkbox_is_register_receipt === this.paymentLines[0].payment_method.kw_checkbox_is_register_receipt) {
                        super.addNewPaymentLine(...arguments);
                    } else {
                      this.showPopup('ErrorPopup', {
                          title : this.env._t('This method can\'t be used for this receipt'),
                          body  : this.env._t('You should not use payment method with tax calculation function and without tax calculation function'),
                      });
                      return;
                    }
                } else {
                      this.showPopup('ErrorPopup', {
                          title : this.env._t('This method can\'t be used for this receipt'),
                          body  : this.env._t('You should choose acceptable payment method'),
                      });
                      return;
                }
            }
            _updateSelectedPaymentline() {
                if (this.paymentLines.every((line) => line.paid)) {
                    this.showPopup('ErrorPopup', {
                              title : this.env._t("Chose payment method"),
                              body  : this.env._t("Sorry, you should choose the same payment method"),
                          });
                          return;
                } else {
                    console.log('this.paymentLines', this.paymentLines)
                    super._updateSelectedPaymentline(...arguments);
                }
            }
        }
    Registries.Component.extend(PaymentScreen, KwPaymentScreen);

    return PaymentScreen;
});
