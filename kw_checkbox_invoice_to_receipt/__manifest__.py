{
    'name': 'CheckBox by Invoice',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '14.0.1.0.3',

    'depends': ['kw_checkbox_product',
                'kw_checkbox_account',
                'account',
                ],

    'data': [
        'security/ir.model.access.csv',

        'wizard/account_payment_register_views.xml',
        'views/receipt_views.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',

    ],
    'installable': True,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
}
