from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    open_revision_count = fields.Integer(
        string='Project Revisions',
        compute='_compute_open_revision_count'
    )

    lead_id = fields.Many2one(
        'crm.lead',
        string="Opportunity",
        required=True,
        ondelete='cascade'
    )

    revision_ids = fields.One2many(
        'project.revision',
        'project_id',
    )
    def _compute_open_revision_count(self):
        for project in self:
            project.open_revision_count = self.env['project.revision'].search_count([('project_id', '=', project.id)])

    def action_open_project_revision_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Revisions',
            'res_model': 'project.revision',
            'view_mode': 'tree,form',
            'target': 'current',
        }
