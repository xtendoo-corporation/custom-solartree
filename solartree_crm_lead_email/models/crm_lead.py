from odoo import _, models, fields, api

class CrmLead(models.Model):
    _inherit = "crm.lead"

    all_users_emails = fields.Char(string="All Users Emails", compute="_compute_all_users_emails")
    business_director_email = fields.Char(string="Business Director Email", compute="_compute_email_business_director")
    business_user_email = fields.Char(string="Business User Email", compute="_compute_email_business_user")
    technical_office_director_email = fields.Char(string="Technical Office Director Email", compute="_compute_email_technical_office_director")
    technical_office_user_email = fields.Char(string="Technical Office User Email", compute="_compute_email_technical_office_user")
    project_url = fields.Char(string="Project URL", compute="_compute_project_url")
    user_id_email = fields.Char(string="User Email", related="user_id.email", store=True)

    def _compute_all_users_emails(self):
        res = self.env['res.users'].search_read([], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.all_users_emails = ','.join(emails)

    # emails to group solartree_crm_lead_automatization.group_crm_business_director
    def _compute_email_business_director(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_business_director').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.email_to = ','.join(emails)

    # emails to group solartree_crm_lead_automatization.group_crm_business_user
    def _compute_email_business_user(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_business_user').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.email_to = ','.join(emails)

    #solartree_crm_lead_automatization.group_crm_technical_office_director
    def _compute_email_technical_office_director(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_technical_office_director').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.email_to = ','.join(emails)

    #solartree_crm_lead_automatization.group_crm_technical_office_user
    def _compute_email_technical_office_user(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_technical_office_user').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.email_to = ','.join(emails)

    def _compute_project_url(self):
        """Compute the dynamic URL for the project."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.project_url = f"{base_url}/web?debug=1#id={record.id}&menu_id=560&cids=1-24-28-29-32&action=832&model=crm.lead&view_type=form"

    def action_crm_lead_send_email_won(self):
        self.ensure_one()
        template = self.env.ref("solartree_crm_lead_email.mail_template_data_crm_lead_email_won", False)
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

    def action_crm_lead_send_email_request(self):
        self.ensure_one()
        template = self.env.ref("solartree_crm_lead_email.mail_template_data_crm_lead_email_request", False)
        compose_form = self.env.ref("mail.email_compose_message_wizard_form")
        ctx = dict(
            default_model="crm.lead",
            default_res_ids=[self.id],  # Cambiado a default_res_ids con una lista
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
