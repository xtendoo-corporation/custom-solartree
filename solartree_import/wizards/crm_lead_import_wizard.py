from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import xlrd


class ImportCrmLead(models.TransientModel):
    _name = 'import.crm.lead.wizard'
    _description = 'Wizard para importar leads desde un archivo XLS'

    file = fields.Binary('Subir archivo XLS', required=True)
    file_name = fields.Char('Nombre del archivo')

    def action_import_crm_lead(self):
        if not self.file:
            raise UserError("Por favor, sube un archivo XLS.")

        # Decodificar el archivo XLS
        data = base64.b64decode(self.file)
        book = xlrd.open_workbook(file_contents=data)
        sheet = book.sheet_by_index(0)

        # Obtener los encabezados de las columnas
        headers = sheet.row_values(0)
        header_indices = {header: index for index, header in enumerate(headers)}

        for row in range(1, sheet.nrows):
            row_values = sheet.row_values(row)
            crm_lead_data = {
                'solartree_code': row_values[header_indices['Codigo_Oferta']],
            }
            if not self.existing_record('crm.lead', crm_lead_data):
                self.create_record('crm.lead', crm_lead_data)

            # Limpiar la sesión de base de datos
        self.env.cr.flush()

    def create_record(self, model_name, model_data):
        try:
            # Si no existe un registro con el mismo 'name', lo crea
            new_record = self.env[model_name].create(model_data)
            print(f"Registro creado exitosamente en el modelo {model_name} con nombre '{model_data.get('name')}'")
            return new_record  # Devuelve el nuevo registro creado

        except Exception as e:
            record_name = model_data.get('name', 'desconocido')
            print(f"Error al crear el registro en el modelo {model_name} con nombre '{record_name}': {e}")

    def existing_record(self, model_name, data):
        existing_record = self.env[model_name].search([('name', '=', data.get('name'))], limit=1)
        if existing_record:
            print(
                f"El registro con el nombre '{data.get('name')}' ya existe en el modelo {model_name}. No se creó un nuevo registro.")
            return existing_record

    # Ejemplos de cómo llamar al método para cada caso:

    # Crear un lead
    # self.create_record('crm.lead', lead_data)

    # Crear un canal de lead
    # self.create_record('crm.lead.channel', channel_data)
