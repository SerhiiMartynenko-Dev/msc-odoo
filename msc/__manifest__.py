# -*- coding: utf-8 -*-
{
    'name': "MSC",
    'version': '14.0.1.5.9',
    'category': 'CRM',
    'application': True,
    'installable': True,
    'auto_install': False,

    'depends': [
        'sale_management',
        'sale_margin',
        'purchase',
        'stock_landed_costs',
        'account',
        'sale_stock',

        'product_tags',
        'web_search_filters_ext',
    ],

    'website': "http://runbins.com",
    'author': "Maksym Nastenko <m.nastenko@runbins.com>",

    'summary': """MSC module""",


    'data': [
        'security/msc_security.xml',
        'security/ir.model.access.csv',


        'data/msc_data.xml',
        'data/report_paperformat_data.xml',
        'data/sale_data.xml',


        'report/product_label_templates.xml',
        'report/receipt_templates.xml',


        'views/msc_templates.xml',


        'views/account_move_view.xml',
        'views/product_views.xml',
        'views/purchase_views.xml',
        'views/res_config_settings_views.xml',
        'views/sale_views.xml',
        'views/stock_picking_views.xml',


        'wizard/wizard_order_set_discount_views.xml',
        'wizard/wizard_print_product_label_views.xml',
    ],


    'qweb': [

    ],
}

