from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import xlrd

class ImportCrmLeadPartial(models.TransientModel):
    _name = 'import.crm.lead.partial.wizard'
    _description = 'Wizard para actualizar leads desde un archivo XLS'

    file = fields.Binary('Subir archivo XLS', required=True)
    file_name = fields.Char('Nombre del archivo')
    error_log = fields.Text('Errores', readonly=True)

    def action_import_crm_lead_partial_wizard(self):
        if not self.file:
            raise UserError("Por favor, sube un archivo XLS.")

        data = base64.b64decode(self.file)
        book = xlrd.open_workbook(file_contents=data)
        sheet = book.sheet_by_index(0)
        headers = sheet.row_values(0)
        header_indexes = {header: index for index, header in enumerate(headers)}

        for row in range(1, sheet.nrows):
            row_values = sheet.row_values(row)
            offer_name = row_values[header_indexes['Nombre de la oferta']]
            commercial_nif = row_values[header_indexes['Comercial']]
            internal_channel_nif = row_values[header_indexes['Canal interno']]

            crm_lead = self.env['crm.lead'].search([('name', '=', offer_name)], limit=1)
            if crm_lead:
                commercial_user = self.get_user_by_nif(commercial_nif)
                internal_channel_user = self.get_user_by_nif(internal_channel_nif)

                if commercial_user:
                    crm_lead.user_id = commercial_user.id
                if internal_channel_user:
                    crm_lead.solartree_intern_channel = internal_channel_user.id

                for header in headers:
                    if header.startswith('R') and '-Técnico OT' in header:
                        revision_prefix = header.split('-')[0]
                        tecnico_ot_nif = row_values[header_indexes[header]]
                        tecnico_ot_user = self.get_user_by_nif(tecnico_ot_nif)
                        if tecnico_ot_user:
                            revision_data = {
                                'offer_tot': tecnico_ot_user.id,
                            }
                            revision_record = self.env['crm.lead.revision'].search([
                                ('lead_id', '=', crm_lead.id),
                                ('name', '=', revision_prefix)
                            ], limit=1)
                            if revision_record:
                                revision_record.write(revision_data)

    def get_user_by_nif(self, nif):
        employee = self.env['hr.employee'].search([('identification_id', '=', nif)], limit=1)
        return employee.user_id if employee else None
