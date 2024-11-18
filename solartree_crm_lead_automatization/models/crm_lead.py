from odoo import _, models, fields, api
from odoo.exceptions import AccessError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def write(self, vals):
        if 'stage_id' in vals:
            # Obtiene la nueva etapa
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])
            # Obtiene el usuario actual
            current_user = self.env.user
            # Verifica si el usuario pertenece al grupo específico
            is_business_director = current_user.has_group('solartree_crm_lead_automatization.group_crm_business_director')
            is_business_user = current_user.has_group('solartree_crm_lead_automatization.group_crm_business_user')
            is_technical_office_director = current_user.has_group('solartree_crm_lead_automatization.group_crm_technical_office_director')
            is_technical_office_user = current_user.has_group('solartree_crm_lead_automatization.group_crm_technical_office_user')

            # Restringe si el usuario no pertenece al grupo requerido y el nuevo estado es "Revisar"
            for record in self:
                if not is_business_director and new_stage.name == "Revisar":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Revisar'."))

        # Continúa con la lógica normal de escritura
        return super(CrmLead, self).write(vals)
