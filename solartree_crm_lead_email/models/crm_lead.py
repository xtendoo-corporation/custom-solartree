from odoo import _, models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    all_users_emails = fields.Char(string="All Users Emails", compute="_compute_all_users_emails")

    def _compute_all_users_emails(self):
        res = self.env['res.users'].search_read([], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.all_users_emails = ','.join(emails)

    def action_crm_lead_send_email(self):
        self.ensure_one()
        template = self.env.ref("solartree_crm_lead_email.mail_template_data_crm_lead_email", False)
        compose_form = self.env.ref("mail.email_compose_message_wizard_form")
        ctx = dict(
            default_model="crm.lead",
            default_res_ids=self.ids,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }
