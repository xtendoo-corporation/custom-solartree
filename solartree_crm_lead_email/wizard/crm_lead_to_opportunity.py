from odoo import api, fields, models, _


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    # def action_apply(self):
    #     self.action_crm_lead_send_email_create_lead()
    #     res = super(Lead2OpportunityPartner, self).action_apply()
    #     return res

    def action_crm_lead_send_email_create_lead(self):
        self.ensure_one()

        # Referencia al template de correo
        template = self.env.ref("solartree_crm_lead_email.mail_template_data_crm_lead_email_create_lead", False)

        # Verificamos si el template está presente
        if template:
            # Enviar el correo asociado al lead
            template.send_mail(self.lead_id.id, force_send=True)

        # Referencia al formulario de composición de correo
        compose_form = self.env.ref("mail.email_compose_message_wizard_form")

        # Creamos el contexto para la ventana del correo
        ctx = dict(
            default_model="crm.lead",
            default_res_ids=[self.lead_id.id],  # Usamos el ID del lead actual
            default_use_template=bool(template),
            default_template_id=template.id if template else False,
            default_composition_mode="comment",
        )
        # Devolvemos la acción para abrir la ventana de composición del correo
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
