{
    'name': 'CheckBox in Point of Sale',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '14.0.1.0.5',

    'depends': ['kw_checkbox_product', 'point_of_sale',
                'kw_checkbox_account', ],

    'data': [
        'security/ir.model.access.csv',

        'wizard/wizard_offline_mode_view.xml',

        'views/checkbox_category_views.xml',
        'views/cash_register_views.xml',
        'views/pos_config_views.xml',
        'views/shift_views.xml',
        'views/pos_order_view.xml',
        'views/pos_session_views.xml',
        'views/pos_payment_method_view.xml',
        'views/pos_assets_common.xml',
        'views/point_of_sale_dashboard.xml',
    ],
    'qweb': [
        'static/src/xml/Screens/ProductScreen/NumpadWidget.xml',
        'static/src/xml/Screens/PaymentScreen/PaymentScreenNumpad.xml',
        'static/src/xml/Screens/PaymentScreen/PaymentScreen.xml',
        'static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
    ],
    'installable': True,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
}
