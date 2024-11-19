from odoo import _, models, fields, api

class CrmLeadRevision(models.Model):
    _inherit = "crm.lead.revision"

    def action_crm_lead_revision_send_email(self):
        print("*"*100)

