from odoo import _, models, fields, api
from odoo.exceptions import AccessError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    approval_margin = fields.Boolean(string="Autorizar bajada de margenes")

    def compare_expenses_and_percentage(self):
        for offer_record in self.selected_revision_id.offer_class_id:
            structure_expenses = offer_record.structure_expenses
            for price_record in self.selected_revision_id.revision_price_ids:
                if price_record.type_price_id.name == "Gastos de estructura":
                    percentage = price_record.percentage
                    if structure_expenses >= percentage:
                        continue
                    return False
        return True

    def compare_profit_and_percentage(self):
        for offer_record in self.selected_revision_id.offer_class_id:
            industrial_profit = offer_record.industrial_profit
            for price_record in self.selected_revision_id.revision_price_ids:
                if price_record.type_price_id.name == "Beneficio Industrial":
                    percentage = price_record.percentage
                    if industrial_profit >= percentage:
                        continue
                    return False
        return True

    def write(self, vals):
        if 'stage_id' in vals:
            # Obtiene la nueva etapa
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])
            # Obtiene el usuario actual
            current_user = self.env.user
            # Verifica si el usuario pertenece al grupo específico
            print("*" * 50)
            is_business_director = current_user.has_group(
                'solartree_crm_lead_automatization.group_crm_business_director')
            # print('is_business_director', is_business_director)
            is_business_user = current_user.has_group('solartree_crm_lead_automatization.group_crm_business_user')
            # print('is_business_user', is_business_user)
            is_technical_office_director = current_user.has_group(
                'solartree_crm_lead_automatization.group_crm_technical_office_director')
            # print('is_technical_office_director', is_technical_office_director)
            is_technical_office_user = current_user.has_group(
                'solartree_crm_lead_automatization.group_crm_technical_office_user')
            # print('is_technical_office_user', is_technical_office_user)
            actual_user_is_same_user_id = self.user_id.id == current_user.id
            # print('actual_user_is_same_user_id', actual_user_is_same_user_id)
            actual_user_is_same_solartree_intern_channel = self.solartree_intern_channel.id == current_user.id
            # print('actual_user_is_same_solartree_intern_channel', actual_user_is_same_solartree_intern_channel)
            actual_user_is_same_offer_tot = self.selected_revision_id.offer_tot.id == current_user.id
            # print('actual_user_is_same_offer_tot', actual_user_is_same_offer_tot)

            for record in self:
                print(f"compare_expenses_and_percentage: {record.compare_expenses_and_percentage()}")
                print(f"compare_profit_and_percentage: {record.compare_profit_and_percentage()}")
                # Solo pueden
                # Director de desarrollo de negocio
                # Usuarios de desarrollo de negocio
                if not is_business_director and new_stage.name == "Nuevo" and not is_business_user:
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'Nuevo'."))

                # Solo pueden
                # Director de desarrollo de negocio
                # Usuarios asignado de desarrollo de negocio (Comercial/user_id)
                if not is_business_director and new_stage.name == "SOLICITADA" and not actual_user_is_same_user_id:
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'SOLICITADA'."))

                # Solo pueden
                # Director de oficina técnica
                # Usuario asignado como canal interno (Canal interno/solartree_intern_channel)
                if not actual_user_is_same_solartree_intern_channel and new_stage.name == "PTE DATOS" and not is_technical_office_director:
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'PTE DATOS'."))

                # Solo puede
                # Director de oficina técnica
                if not is_technical_office_director and new_stage.name == "ESTUDIO":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'ESTUDIO'."))

                # Solo puede
                # Usuario asignado como Técnico OT en la Revision(Técnico OT/selected_revision_id.offer_tot)
                if new_stage.name == "ENTREGADA":
                    # Verifica si el usuario tiene el permiso adecuado
                    if not actual_user_is_same_offer_tot:
                        raise AccessError(
                            _("No tienes permiso para cambiar el estado a 'ENTREGADA': Usuario no autorizado."))
                    # Si el usuario tiene permiso, verificamos si approval_margin es False
                    if not record.approval_margin:
                        # Si approval_margin es False, las comparaciones deben cumplirse
                        if record.compare_expenses_and_percentage():
                            raise AccessError(
                                _("No tienes permiso para cambiar el estado a 'ENTREGADA': Gastos de estructura no cumplen con los márgenes aprobados."))
                        if record.compare_profit_and_percentage():
                            raise AccessError(
                                _("No tienes permiso para cambiar el estado a 'ENTREGADA': Beneficio Industrial no cumple con los márgenes aprobados."))

                # Solo puede
                # Usuario asignado de desarrollo de negocio (Comercial/user_id)
                if not actual_user_is_same_user_id and new_stage.name == "PRESENTADA":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'PRESENTADA'."))

                # Solo puede
                # Director de desarrollo de negocio
                if not is_business_director and new_stage.name == "PERDIDA":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'PERDIDA'."))

                # Solo puede
                # Director de desarrollo de negocio
                if not is_business_director and new_stage.name == "ADJUDICADA":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'ADJUDICADA'."))

                # Solo puede
                # Director de desarrollo de negocio
                if not is_business_director and new_stage.name == "CONTRATADA":
                    raise AccessError(_("No tienes permiso para cambiar el estado a 'CONTRATADA'."))

        return super(CrmLead, self).write(vals)
