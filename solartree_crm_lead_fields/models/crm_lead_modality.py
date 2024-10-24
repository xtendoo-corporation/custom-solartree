from odoo import fields, models

class CrmLeadModality(models.Model):
    _name = "crm.lead.modality"
    _description = "Lead Modality"

    name = fields.Char(
        string="Modality Name",
        required=True
    )
