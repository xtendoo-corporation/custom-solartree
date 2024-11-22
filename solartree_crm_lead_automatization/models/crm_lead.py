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

    def _obtain_allowed_users(self, stage):
        """Devuelve los IDs de los usuarios permitidos para la etapa proporcionada."""
        allowed_users = set()
        current_user = self.env.user
        error_messages = []  # Lista para almacenar los mensajes de error

        # Obtener usuarios permitidos por grupos
        for group in stage.allowed_groups:
            users = self.env['res.users'].search([('groups_id', 'in', group.id)])
            allowed_users.update(users.ids)  # Agregar IDs de usuarios al conjunto
            if current_user.id not in users.ids:
                error_messages.append(_("El usuario actual no tiene privilegios del grupo: '%s'" % group.name))

        # Comprobar si el usuario actual cumple con user_offer_tot_required
        if stage.user_offer_tot_required:
            for record in self:
                if record.selected_revision_id.offer_tot.id == current_user.id:
                    allowed_users.add(current_user.id)
            if current_user.id not in allowed_users:
                error_messages.append(
                    _("El usuario actual no es 'Tecnico OT' de la revisión."))

        # Comprobar si el usuario actual cumple con user_id_required
        if stage.user_id_required:
            for record in self:
                if record.user_id.id == current_user.id:
                    allowed_users.add(current_user.id)
            if current_user.id not in allowed_users:
                error_messages.append(_("El usuario actual no es comercial de esta oferta."))

        return allowed_users, error_messages

    def write(self, vals):
        if 'stage_id' in vals:
            # Obtiene la nueva etapa
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])

            ###################EL CLIENTE INDICA QUE NO SE DEBE PROHIBIR EL SALTO DE MAS DE UNA ETAPA###################
            # Prohibir el salto de mas de una etapa
            # if self.stage_id.sequence + 1 < new_stage.sequence or self.stage_id.sequence - 1 > new_stage.sequence:
            #     raise AccessError(_("No puedes saltar más de una etapa."))
            ############################################################################################################

            # Obtener los usuarios permitidos y los mensajes de error
            allowed_users, error_messages = self._obtain_allowed_users(new_stage)
            if self.env.user.id not in allowed_users:
                # Si el usuario actual no está permitido, lanzar un error con los detalles
                error_msg = _(
                    "No tienes permiso para cambiar a la etapa '%s'. Los siguientes errores ocurrieron: " % new_stage.name)
                error_msg += "\n".join(error_messages)
                raise AccessError(error_msg)

            # Comprobar si la etapa requiere aprobación de margen
            if self.stage_id.margin_approval_required:
                if not self.approval_margin:
                    if self.compare_expenses_and_percentage():
                        raise AccessError(
                            _("No tienes permiso para cambiar a la etapa '%s': Gastos de estructura no cumplen con los márgenes aprobados." % new_stage.name))
                    if self.compare_profit_and_percentage():
                        raise AccessError(
                            _("No tienes permiso para cambiar a la etapa '%s': Beneficio Industrial no cumple con los márgenes aprobados." % new_stage.name))

        return super(CrmLead, self).write(vals)
