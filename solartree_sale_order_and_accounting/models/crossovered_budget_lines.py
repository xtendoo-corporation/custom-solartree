from odoo import models, fields

class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line'
    )
    coste = fields.Float(
        related='sale_order_line_id.purchase_price',
        string='Coste',
        store=True
    )

