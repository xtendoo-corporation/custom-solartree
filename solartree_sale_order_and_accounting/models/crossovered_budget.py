from odoo import models, fields, api

class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    project_id = fields.Many2one('project.project', string='Project')

    @api.model_create_multi
    def create(self, vals_list):
        budgets = super().create(vals_list)
        if len(budgets) == 1 and self.env.context.get('project_update'):  # Creation with Add Budget button in project update
            budgets.action_budget_confirm()
        return budgets
