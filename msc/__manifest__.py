# -*- coding: utf-8 -*-
{
    'name': "MSC",
    'version': '14.0.1.7.0',
    'category': 'CRM',
    'application': True,
    'installable': True,
    'auto_install': False,

    'depends': [
        'account',
        'crm',
        'purchase',
        'sale_management',
        'sale_margin',
        'sale_stock',
        'stock_account',
        'stock_landed_costs',

        'kw_checkbox_invoice_to_receipt',
        'web_ir_actions_act_multi',

        'product_tags',
        'web_search_filters_ext',
    ],

    'website': "https://runbins.com",
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
        'views/crm_team_views.xml',
        'views/product_views.xml',
        'views/product_pricelist_views.xml',
        'views/purchase_views.xml',
        'views/receipt_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_bank_views.xml',
        'views/res_partner_views.xml',
        'views/sale_views.xml',
        'views/stock_inventory_views.xml',
        'views/stock_picking_views.xml',


        'wizard/wizard_order_set_discount_views.xml',
        'wizard/wizard_print_product_label_views.xml',
        'wizard/wizard_print_receipt_views.xml',
        'wizard/wizard_reassessment_views.xml',
    ],
}

