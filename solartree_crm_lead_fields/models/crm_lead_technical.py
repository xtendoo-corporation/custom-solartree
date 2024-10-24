from odoo import fields, models

class CrmLeadTechnical(models.Model):
    _name = "crm.lead.technical"
    _description = "Lead Technical"

    name = fields.Char(
        string="Technical Name",
        required=True
    )
