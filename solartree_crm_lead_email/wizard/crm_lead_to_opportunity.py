from odoo import api, fields, models, _


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    def action_crm_lead_send_email_create_lead(self):
        self.ensure_one()
        # Referencia al template de correo
        template = self.env.ref("solartree_crm_lead_email.mail_template_data_crm_lead_email_create_lead", False)
        if template:
            template.send_mail(res_id=None, force_send=True)
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


    # def action_crm_lead_send_email_create_lead(self):
    #     self.ensure_one()
    #     template = self.env.ref("solartree_crm_lead_email.mail_template_data_crm_lead_email_create_lead", False)
    #     compose_form = self.env.ref("mail.email_compose_message_wizard_form")
    #     ctx = dict(
    #         default_model="crm.lead2opportunity.partner",
    #         default_res_ids=self.ids,
    #         default_use_template=bool(template),
    #         default_template_id=template and template.id or False,
    #         default_composition_mode="comment",
    #     )
    #     return {
    #         "name": _("Compose Email"),
    #         "type": "ir.actions.act_window",
    #         "view_mode": "form",
    #         "res_model": "mail.compose.message",
    #         "views": [(compose_form.id, "form")],
    #         "view_id": compose_form.id,
    #         "target": "new",
    #         "context": ctx,
    #     }

    # def action_crm_lead_send_email_create_lead(self):
    #     self.ensure_one()
    #
    #     # Obtener el registro relacionado de crm.lead
    #     lead = self.env['crm.lead'].browse(self.env.context.get('active_id'))
    #
    #     if not lead.exists():
    #         raise UserError(_("El registro de la oportunidad no existe o ha sido eliminado."))
    #
    #     template = self.env.ref("solartree_crm_lead_email.mail_template_data_crm_lead_email_create_lead", False)
    #     compose_form = self.env.ref("mail.email_compose_message_wizard_form")
    #
    #     ctx = dict(
    #         default_model="crm.lead",
    #         default_res_ids=[lead.id],  # Cambiar a `default_res_ids`
    #         default_use_template=bool(template),
    #         default_template_id=template and template.id or False,
    #         default_composition_mode="comment",
    #     )
    #
    #     return {
    #         "name": _("Compose Email"),
    #         "type": "ir.actions.act_window",
    #         "view_mode": "form",
    #         "res_model": "mail.compose.message",
    #         "views": [(compose_form.id, "form")],
    #         "view_id": compose_form.id,
    #         "target": "new",
    #         "context": ctx,
    #     }
