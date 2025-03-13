import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ProjectTaskInherited(models.Model):
    _inherit = 'project.task'

    start_date_planned = fields.Date(string='Planned Start Date')
    date_end = fields.Date(string='Date End')

    def copy(self, default=None):
        default = dict(default or {})
        default["message_ids"] = False
        return super(ProjectTaskInherited, self).copy(default)
