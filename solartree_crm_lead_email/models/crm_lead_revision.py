from odoo import _, models, fields, api

class CrmLeadRevision(models.Model):
    _inherit = "crm.lead.revision"

    all_users_emails = fields.Char(string="All Users Emails", compute="_compute_all_users_emails")


    def _compute_all_users_emails(self):
        res = self.env['res.users'].search_read([], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.all_users_emails = ','.join(emails)

    def action_crm_lead_revision_send_email(self):
        print("*"*100)




