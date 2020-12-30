# -*- coding: utf-8 -*-
{
    'name': "Product Tags",
    'version': '14.0.1.0.0',
    'category': 'Hidden',
    'application': False,
    'installable': True,
    'auto_install': False,


    'depends': [
        'sale',
    ],


    'website': "http://runbins.com",
    'author': "Maksym Nastenko <m.nastenko@runbins.com>",

    'summary': """Add tags for products""",


    'data': [
        'security/ir.model.access.csv',


        'views/product_views.xml',
    ],

}

