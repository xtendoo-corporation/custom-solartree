from odoo import fields, models

class CrmLeadChannel(models.Model):
    _name = "crm.lead.channel"
    _description = "Lead Channel"

    name = fields.Char(
        string="Channel Name",
        required=True
    )
