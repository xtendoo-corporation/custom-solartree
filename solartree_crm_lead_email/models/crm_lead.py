from odoo import _, models, fields, api

class CrmLead(models.Model):
    _inherit = "crm.lead"

    all_users_emails = fields.Char(string="All Users Emails", compute="_compute_all_users_emails")
    solar_tree_director_email = fields.Char(string="Solar Tree Director Email", compute="_compute_email_solartree_director")
    #Grupos de desarrollo de negocio
    business_director_email = fields.Char(string="Business Director Email", compute="_compute_email_business_director")
    business_user_email = fields.Char(string="Business User Email", compute="_compute_email_business_user")
    #Grupos de oficina técnica
    technical_office_director_email = fields.Char(string="Technical Office Director Email", compute="_compute_email_technical_office_director")
    technical_office_user_email = fields.Char(string="Technical Office User Email", compute="_compute_email_technical_office_user")
    #Comercial de la oferta
    user_id_email = fields.Char(string="User Email", related="user_id.email", store=True)
    #Tecnico de la revisión seleccionada
    assigned_revision_tecnical_email = fields.Char(string="Assigned Revision Tecnical", related="selected_revision_id.offer_tot.email", store=True)
    #condiciones
    users_closest_offer = fields.Char(string="Users Closest Offert", compute="_compute_users_emails_closest_offert")
    users_closest_offer_meeting = fields.Char(string="Users Closest Offert Meeting", compute="_compute_users_emails_closest_offert_meeting")
    #URL del proyecto
    project_url = fields.Char(string="Project URL", compute="_compute_project_url")

    def _compute_users_emails_closest_offert(self):
        for record in self:
            emails = set()
            for group in record.selected_revision_id.offer_class_id.res_group_mail_ids:
                users = self.env['res.users'].search([('groups_id', 'in', group.id)])
                emails.update(user.email for user in users if user.email)
            record.users_closest_offer = ','.join(emails)

    def _compute_users_emails_closest_offert_meeting(self):
        for record in self:
            emails = set()
            for group in record.selected_revision_id.offer_class_id.res_group_meet_ids:
                users = self.env['res.users'].search([('groups_id', 'in', group.id)])
                emails.update(user.email for user in users if user.email)
            record.users_closest_offer_meeting = ','.join(emails)

    def _compute_all_users_emails(self):
        res = self.env['res.users'].search_read([], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.all_users_emails = ','.join(emails)

    def _compute_email_solartree_director(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_solartree_director').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.solar_tree_director_email = ','.join(emails)


    # emails to group solartree_crm_lead_automatization.group_crm_business_director
    def _compute_email_business_director(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_business_director').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.business_director_email = ','.join(emails)

    # emails to group solartree_crm_lead_automatization.group_crm_business_user
    def _compute_email_business_user(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_business_user').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.business_user_email = ','.join(emails)

    #solartree_crm_lead_automatization.group_crm_technical_office_director
    def _compute_email_technical_office_director(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_technical_office_director').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.technical_office_director_email = ','.join(emails)

    #solartree_crm_lead_automatization.group_crm_technical_office_user
    def _compute_email_technical_office_user(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_technical_office_user').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.technical_office_user_email = ','.join(emails)

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
