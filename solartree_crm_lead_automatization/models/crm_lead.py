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
            print("*"*50)
            is_business_director = current_user.has_group('solartree_crm_lead_automatization.group_crm_business_director')
            print('is_business_director', is_business_director)
            is_business_user = current_user.has_group('solartree_crm_lead_automatization.group_crm_business_user')
            print('is_business_user', is_business_user)
            is_technical_office_director = current_user.has_group('solartree_crm_lead_automatization.group_crm_technical_office_director')
            print('is_technical_office_director', is_technical_office_director)
            is_technical_office_user = current_user.has_group('solartree_crm_lead_automatization.group_crm_technical_office_user')
            print('is_technical_office_user', is_technical_office_user)
            actual_user_is_same_user_id = self.user_id.id == current_user.id
            print('actual_user_is_same_user_id', actual_user_is_same_user_id)
            actual_user_is_same_solartree_intern_channel = self.solartree_intern_channel.id == current_user.id
            print('actual_user_is_same_solartree_intern_channel', actual_user_is_same_solartree_intern_channel)

            # Restringe si el usuario no pertenece al grupo requerido y el nuevo estado es "Revisar"
            for record in self:

                # Solo pueden
                # Director de desarrollo de negocio
                # Usuarios de desarrollo de negocio
                if not is_business_director and new_stage.name == "Nuevo" and not is_business_user:
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Nuevo'."))

                # Solo pueden
                # Director de desarrollo de negocio
                # Usuarios asignado de desarrollo de negocio (comercial/user_id)
                if not is_business_director and new_stage.name == "Leads KO" and not actual_user_is_same_user_id:
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Leads KO'."))

                # Solo pueden
                # Director de desarrollo de negocio
                # Usuarios asignado de desarrollo de negocio (Comercial/user_id)
                if not is_business_director and new_stage.name == "Solicitado Estudio" and not actual_user_is_same_user_id:
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Solicitado Estudio'."))

                # Solo pueden
                # Director de oficina técnica
                # Usuario asignado como canal interno (Canal interno/solartree_intern_channel)
                if not actual_user_is_same_solartree_intern_channel and new_stage.name == "Pte Datos" and not is_technical_office_director:
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Pte Datos'."))

                # Solo puede
                # Director de oficina técnica
                if not is_technical_office_director and new_stage.name == "Estudio":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Estudio'."))

                # Solo pueden
                # Director de oficina técnica
                # Usuario asignado como canal interno (Canal interno/solartree_intern_channel)
                if not is_technical_office_director and new_stage.name == "No ofertable" and not actual_user_is_same_solartree_intern_channel:
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'No ofertable'."))

                # Solo puede
                # Usuario asignado como canal interno (Canal interno/solartree_intern_channel)
                if not actual_user_is_same_solartree_intern_channel and new_stage.name == "Entregada":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Entregada'."))

                # Solo puede
                # Usuario asignado de desarrollo de negocio (Comercial/user_id)
                if not actual_user_is_same_user_id and new_stage.name == "Presentada":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Presentada'."))

                # Solo puede
                # Director de desarrollo de negocio
                if not is_business_director and new_stage.name == "Perdida":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Perdida'."))

                # Solo puede
                # Director de desarrollo de negocio
                if not is_business_director and new_stage.name == "Adjudicada":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Adjudicada'."))

                # Solo puede
                # Director de desarrollo de negocio
                if not is_business_director and new_stage.name == "Contratada":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Contratada'."))

                # Solo puede
                # Director de desarrollo de negocio
                if not is_business_director and new_stage.name == "Stand By":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Stand By'."))

        return super(CrmLead, self).write(vals)
