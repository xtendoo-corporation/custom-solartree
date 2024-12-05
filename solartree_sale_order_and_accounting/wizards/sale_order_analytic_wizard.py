from odoo import models, fields, api

class SaleOrderAnalyticWizard(models.TransientModel):
    _name = 'sale.order.analytic.wizard'
    _description = 'Sale Order Analytic Wizard'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    def action_apply(self):
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if not sale_order:
            return

        budget = self.env['crossovered.budget'].create({
            'name': f'Budget for {sale_order.name}',
            'date_from': self.date_start,
            'date_to': self.date_end,
        })

        for line in sale_order.order_line:
            self.env['crossovered.budget.lines'].create({
                'crossovered_budget_id': budget.id,
                'analytic_account_id': self.analytic_account_id.id,
                'sale_order_line_id': line.id,
                'date_from': self.date_start,
                'date_to': self.date_end,
                'planned_amount': line.purchase_price,
                'general_budget_id': line.product_id.id,
                'name': sale_order.name,
            })
