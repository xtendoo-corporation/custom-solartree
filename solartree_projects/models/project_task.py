from odoo import models, fields

class ProjectTaskInherited(models.Model):
    _inherit = 'project.task'

    start_date_planned = fields.Date(
        string='Planned Start Date'
    )
    date_end = fields.Date(
        string='Date End'
    )
