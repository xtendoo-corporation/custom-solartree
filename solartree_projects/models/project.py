from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    open_revision_count = fields.Integer(
        string='Project Revisions',
        compute='_compute_open_revision_count'
    )

    revision_ids = fields.One2many(
        'project.revision',
        'project_id',
    )

    partner_id_lead = fields.Many2one(
        'res.partner',
        string="Partner",
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string="Opportunity",
    )

    selected_revision_id = fields.Many2one(
        'project.revision',
        string="Selected Revision",
        domain="[('project_id', '=', id)]",
    )
    offer_kwp = fields.Float(
        related='selected_revision_id.offer_kwp',
        string='Offer kWp',
        readonly=False
    )
    offer_kwn = fields.Float(
        related='selected_revision_id.offer_kwn',
        string='Offer kWn',
        readonly=False
    )
    offer_class = fields.Char(
        string='Offer Class',
        store=True,
        readonly=False,
    )

    start_date_planned = fields.Date(
        string='Planned Start Date',
        compute='_compute_start_date_planned',
        store=True
    )

    @api.depends('task_ids', 'task_ids.start_date_planned')
    def _compute_start_date_planned(self):
        for project in self:
            installation_tasks = project.task_ids.filtered(lambda t: t.tag_ids[:1].name == 'INSTALACIÓN')
            print("*" * 80)
            print(installation_tasks)
            if installation_tasks:
                project.start_date_planned = installation_tasks[0].start_date_planned
                print(project.start_date_planned)
            else:
                project.start_date_planned = False
                print(project.start_date_planned)

    installation_date_end = fields.Date(
        string='Installation date end',
        compute='_compute_installation_date_end',
        store=True
    )

    @api.depends('task_ids', 'task_ids.date_end')
    def _compute_installation_date_end(self):
        for project in self:
            installation_tasks = project.task_ids.filtered(lambda t: 'INSTALACIÓN' in t.tag_ids.mapped('name'))
            if installation_tasks:
                project.installation_date_end = installation_tasks[0].date_end
            else:
                project.installation_date_end = False

    @api.depends('revision_ids.offer_selected')
    def _compute_selected_revision_id(self):
        print("?" * 80)
        print("_compute_selected_revision_id")
        for record in self:
            selected_revision = record.revision_ids.filtered(lambda r: r.offer_selected)
            record.selected_revision_id = selected_revision[:1]

    @api.onchange('revision_ids')
    def _onchange_revision_ids(self):
        print("-" * 80)
        print("Onchange Revision IDs")
        for record in self:
            offer_selected_revisions = record.revision_ids.filtered(lambda r: r.offer_selected)
            if offer_selected_revisions:
                record.selected_revision_id = offer_selected_revisions[0]
            else:
                record.selected_revision_id = False

    def _compute_open_revision_count(self):
        for project in self:
            project.open_revision_count = self.env['project.revision'].search_count([('project_id', '=', project.id)])

    def action_open_project_revision_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Revisions',
            'res_model': 'project.revision',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
            'target': 'current',
        }
