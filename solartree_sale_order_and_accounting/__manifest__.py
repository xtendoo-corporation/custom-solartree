{
    'name': 'Sale Order and Accounting Extension',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Extensions for Sale Orders and Accounting',
    'description': """
        This module provides additional features and extensions for Sale Orders and Accounting in Odoo.
    """,
    'author': 'Xtendoo',
    'depends': [
        'sale',
        'account',
    ],
    'data': [
        'wizards/sale_order_analytic_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,

}
