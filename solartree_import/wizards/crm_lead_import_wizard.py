from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import xlrd


class ImportCrmLead(models.TransientModel):
    _name = 'import.crm.lead.wizard'
    _description = 'Wizard para importar leads desde un archivo XLS'

    file = fields.Binary('Subir archivo XLS', required=True)
    file_name = fields.Char('Nombre del archivo')
    error_log = fields.Text('Errores', readonly=True)

    def action_import_crm_lead(self):
        if not self.file:
            raise UserError("Por favor, sube un archivo XLS.")

        data = base64.b64decode(self.file)
        book = xlrd.open_workbook(file_contents=data)
        sheet = book.sheet_by_index(0)
        headers = sheet.row_values(0)
        header_indexes = {header: index for index, header in enumerate(headers)}

        for row in range(1, sheet.nrows):
            row_values = sheet.row_values(row)
            # Obtener o crear el registro del técnico
            solartree_lead_technical_record = self.get_or_create_record('crm.lead.technical',
                                                                        row_values[header_indexes['Tecnico']])
            solartree_lead_channel_record = self.get_or_create_record('crm.lead.channel',
                                                                      row_values[header_indexes['Oferta_Canal']])
            # Asegúrate de que obtienes un valor en formato de fecha adecuado
            solartree_date_request_record = self.get_date_formatted(row_values[header_indexes['Fecha_Solicitud_Oferta']],book)


            crm_lead_data = {
                'name': row_values[header_indexes['Codigo_Oferta']] + ' - ' + row_values[
                    header_indexes['Identificacion']],
                'type': 'opportunity',
                'solartree_code': row_values[header_indexes['Codigo_Oferta']],
                'solartree_lead_identification': row_values[header_indexes['Identificacion']],
                'solartree_date_request': solartree_date_request_record,  # Usa el valor convertido
                'solartree_lead_channel': solartree_lead_channel_record.id,
                'solartree_lead_technical': solartree_lead_technical_record.id,
            }

            # Crear registro de lead y capturar el ID
            crm_lead_record = self.env['crm.lead'].create(crm_lead_data)

            # Datos comunes para todas las revisiones
            crm_lead_revision_data_common = {
                'solartree_lead_type_id': self.get_or_create_record('crm.lead.type',
                                                                    row_values[header_indexes['Oferta_Tipo']]).id,
                'solartree_lead_modality_id': self.get_or_create_record('crm.lead.modality', row_values[
                    header_indexes['Oferta_Modalidad']]).id,
                'solartree_lead_collective': self.get_boolean_value(row_values[header_indexes['Oferta_Colectivo']]),
                'solartree_lead_storage': self.get_boolean_value(row_values[header_indexes['Oferta_Almacenamiento']]),
                'solartree_lead_scope': self.get_or_create_record('crm.lead.scope',
                                                                  row_values[header_indexes['Oferta_Alcance']]).id,
                'solartree_lead_structure_type': self.get_or_create_record('crm.lead.structure.type', row_values[
                    header_indexes['Oferta_Estructura_Tipo']]).id,
                'solartree_lead_structure_model': self.get_or_create_record('crm.lead.structure.model', row_values[
                    header_indexes['Oferta_Estructura_Modelo']]).id,
            }
            # Crear revisiones R0 a R6 si están activas (valor "1")
            for revision in ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
                if row_values[header_indexes[revision]] == 1:
                    revision_data = self.create_revision(row_values, header_indexes, revision,
                                                                 crm_lead_revision_data_common)
                    # Aquí pasamos el lead_id en el contexto
                    context = dict(self.env.context)
                    context.update({'default_lead_id': crm_lead_record.id})
                    # Crear la revisión pasando el contexto con el default_lead_id
                    self.env['crm.lead.revision'].with_context(context).create(revision_data)
        # Limpiar la sesión de base de datos
        self.env.cr.flush()

    # Metodo para construir los datos de revisión
    def create_revision(self, row_values, header_indices, revision, common_data):
        # Datos específicos de la revisión
        revision_data = {
            'offer_kwp': row_values[header_indices[f'Oferta_kWp-{revision}']],
            'offer_kwn': row_values[header_indices[f'Oferta_kWn-{revision}']],
            'offer_storage_kwh': row_values[header_indices[f'Oferta_Almacenamiento_kWh-{revision}']],
            'offer_storage_kwn': row_values[header_indices[f'Oferta_Almacenamiento_kWn-{revision}']],
            'offer_ve_kwn': row_values[header_indices[f'Oferta_VE_kWn-{revision}']],
            'offer_kwh_year': row_values[header_indices[f'Oferta_kWh_año-{revision}']],
        }

        # Combina los datos comunes con los específicos de la revisión
        return {**common_data, **revision_data}

    def get_date_formatted(self, date_value, book):
        if isinstance(date_value, float):  # Verifica si es un float (el formato típico de fecha en Excel)
            # Convierte el número en una fecha usando xlrd.xldate_as_datetime
            date_as_datetime = xlrd.xldate_as_datetime(date_value, book.datemode)
            return date_as_datetime.strftime('%Y-%m-%d')
        else:
            # Si ya es un string, úsalo directamente
            return date_value

    # Metodo para obtener o crear un registro en un modelo
    @api.model
    def get_or_create_record(self, model_name, name):
        # Buscar el registro en el modelo especificado
        record = self.env[model_name].search([('name', '=', name)], limit=1)
        if not record:
            # Si no existe, crear un nuevo registro
            record = self.env[model_name].create({'name': name})

        return record

    # Metodo que asigna un boolean segun el valor de la celda SI/NO
    def get_boolean_value(self, value):
        if value == 'SÍ':
            return True
        else:
            return False

    # def create_record(self, model_name, model_data):
    #     try:
    #         # Si no existe un registro con el mismo 'name', lo crea
    #         new_record = self.env[model_name].create(model_data)
    #         print(f"Registro creado exitosamente en el modelo {model_name} con nombre '{model_data.get('name')}'")
    #         return new_record  # Devuelve el nuevo registro creado
    #
    #     except Exception as e:
    #         record_name = model_data.get('name', 'desconocido')
    #         print(f"Error al crear el registro en el modelo {model_name} con nombre '{record_name}': {e}")
    #
    # def existing_record(self, model_name, data):
    #     existing_record = self.env[model_name].search([('name', '=', data.get('name'))], limit=1)
    #     if existing_record:
    #         print(
    #             f"El registro con el nombre '{data.get('name')}' ya existe en el modelo {model_name}. No se creó un nuevo registro.")
    #         return existing_record

    # crm_lead_revision_total_price_rx = {
    #     'revision_id': lambda self: self.env['crm.lead.revision'].search([('name', '=', crm_lead_revision_data.get('name'))], limit=1),#Pendiente de revisar
    #     'type_total_price_id': row_values[header_indices['Oferta_Precio_Total_R2']],
    #     'company_currency': self.env.company.currency_id,
    #     'price': row_values[header_indices['Oferta_Precio_Total_R2']],
    # }
