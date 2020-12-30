# -*- coding: utf-8 -*-
{
    'name': "MSC",
    'version': '14.0.1.0.3',
    'category': 'CRM',
    'application': True,
    'installable': True,
    'auto_install': False,

    'depends': [
        'sale',
        'purchase',
        'stock_landed_costs',

        'product_tags',
        'web_search_filters_ext',
    ],

    'website': "http://runbins.com",
    'author': "Maksym Nastenko <m.nastenko@runbins.com>",

    'summary': """MSC module""",


    'data': [
        'security/ir.model.access.csv',


        'data/sale_data.xml',


        'views/msc_templates.xml',


        'views/product_views.xml',
        'views/sale_views.xml',
    ],


    'qweb': [

    ],
}

