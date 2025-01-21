from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_invoice_project(self):
        for line in self.invoice_line_ids:
            if line.analytic_distribution:
                analytic = self.env['account.analytic.account'].search([('id', '=', list(line.analytic_distribution.keys())[0])])
                if analytic:
                    return analytic


