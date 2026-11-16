# -*- coding: utf-8 -*-
{
    'name': 'Ming Brand Theme',
    'version': '19.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Branding theme for Ming Coffee & More on Odoo backend and login',
    'author': 'Ming Coffee',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'ming_customer_care'],
    'data': [
        'views/login_templates.xml',
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ming_brand_theme/static/src/scss/ming_brand.scss',
        ],
        'web.assets_frontend': [
            'ming_brand_theme/static/src/css/ming_login.css',
        ],
    },
    'installable': True,
    'application': False,
}
