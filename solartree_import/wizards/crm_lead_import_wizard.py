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

            # Datos de lead
            crm_lead_data = self.create_crm_lead(row_values, header_indexes, book)
            # Crear registro de lead y capturar el ID
            crm_lead_record = self.env['crm.lead'].create(crm_lead_data)

            # Crear revisiones R0 a R6 si están activas
            for revision in ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
                if row_values[header_indexes[revision]] == 1:
                    # Generar y crear la revisión pasando el contexto con el default_lead_id
                    revision_data = self.create_revision(row_values, header_indexes, revision, book)
                    # Crear el registro de revisión
                    revision_record = self.env['crm.lead.revision'].with_context(default_lead_id=crm_lead_record.id).create(revision_data)
                    # Crear el registro de precios con el porcentaje
                    self.create_fee_and_margins(row_values, header_indexes, revision, revision_record)

        # Limpiar la sesión de base de datos
        self.env.cr.flush()

    @api.model
    def create_crm_lead(self, row_values, header_indexes, book):
        crm_lead_data = {
            'name': row_values[header_indexes['Codigo_Oferta']] + ' - ' + row_values[header_indexes['Identificacion']],
            'type': 'opportunity',
            'solartree_code': row_values[header_indexes['Codigo_Oferta']],
            'solartree_lead_identification': row_values[header_indexes['Identificacion']],
            'solartree_date_request': self.get_date_formatted(row_values[header_indexes['Fecha_Solicitud_Oferta']],
                                                              book),
            'solartree_lead_channel': self.get_or_create_record('crm.lead.channel',
                                                                row_values[header_indexes['Oferta_Canal']]).id,
            'solartree_lead_technical': self.get_or_create_record('crm.lead.technical',
                                                                  row_values[header_indexes['Tecnico']]).id,
        }
        return crm_lead_data

    # Metodo para construir y devolver los datos de revisión (comunes y específicos)
    def create_revision(self, row_values, header_indexes, revision, book):
        # Datos comunes a todas las revisiones
        common_data = {
            'solartree_lead_type_id': self.get_or_create_record('crm.lead.type',
                                                                row_values[header_indexes['Oferta_Tipo']]).id,
            'solartree_lead_modality_id': self.get_or_create_record('crm.lead.modality',
                                                                    row_values[header_indexes['Oferta_Modalidad']]).id,
            'solartree_lead_collective': self.get_boolean_value(row_values[header_indexes['Oferta_Colectivo']]),
            'solartree_lead_storage': self.get_boolean_value(row_values[header_indexes['Oferta_Almacenamiento']]),
            'solartree_lead_scope': self.get_or_create_record('crm.lead.scope',
                                                              row_values[header_indexes['Oferta_Alcance']]).id,
            'solartree_lead_structure_type': self.get_or_create_record('crm.lead.structure.type', row_values[
                header_indexes['Oferta_Estructura_Tipo']]).id,
            'solartree_lead_structure_model': self.get_or_create_record('crm.lead.structure.model', row_values[
                header_indexes['Oferta_Estructura_Modelo']]).id,
        }

        # Datos específicos de la revisión
        specific_data = {
            'offer_kwp': row_values[header_indexes[f'Oferta_kWp-{revision}']],
            'offer_kwn': row_values[header_indexes[f'Oferta_kWn-{revision}']],
            'offer_storage_kwh': row_values[header_indexes[f'Oferta_Almacenamiento_kWh-{revision}']],
            'offer_storage_kwn': row_values[header_indexes[f'Oferta_Almacenamiento_kWn-{revision}']],
            'offer_ve_kwn': row_values[header_indexes[f'Oferta_VE_kWn-{revision}']],
            'offer_kwh_year': row_values[header_indexes[f'Oferta_kWh_año-{revision}']],
            'offer_pb_actual': row_values[header_indexes[f'PB_actuales-{revision}']],
            'offer_tir_actual': row_values[header_indexes[f'TIR_actuales-{revision}']],
            'offer_pb_omip': row_values[header_indexes[f'PB_OMIP-{revision}']],
            'offer_tir_omip': row_values[header_indexes[f'TIR_OMIP-{revision}']],
            'offer_pb_proyection': row_values[header_indexes[f'PB_proyección-{revision}']],
            'offer_tir_proyection': row_values[header_indexes[f'TIR_proyección-{revision}']],
            'offer_tot': self.get_or_create_record('crm.lead.tot', row_values[header_indexes[f'TOT-{revision}']]).id,
            'offer_HT': row_values[header_indexes[f'HT_Oferta-{revision}']],
            'offer_date_deliver': self.get_date_formatted(
                row_values[header_indexes[f'Fecha_Entrega_Oferta-{revision}']], book)
        }
        # Combina los datos comunes con los específicos de la revisión
        return {**common_data, **specific_data}

    @api.model
    def create_fee_and_margins(self, row_values, header_indexes, revision, revision_record):
        # Buscar el registro de tipo de precio "Fee Interno"
        type_fee_and_margins = self.env['crm.lead.revision.global.type'].search([('name', '=', 'Fee Interno')], limit=1)
        # Si no existe, créalo con el comportamiento especificado
        if not type_fee_and_margins:
            type_fee_and_margins = self.env['crm.lead.revision.global.type'].create({
                'name': 'Fee Interno',
                'behavior': 'fee_and_margins',
            })
        # Crear el registro de precios con el porcentaje
        fee_and_margins_data = {
            'revision_id': revision_record.id,  # Usar el ID de la revisión creada
            'type_price_id': type_fee_and_margins.id,
            'percentage': row_values[header_indexes[f'Oferta_Fee_interno_%-{revision}']]
        }
        self.env['crm.lead.revision.prices'].create(fee_and_margins_data)

    # Metodo para construir los datos de inversor
    @api.model
    def create_inversor(self, row_values, header_indexes, revision, common_data, book):
        pass

    @api.model
    def create_battery(self, row_values, header_indexes, revision, common_data, book):
        pass

    @api.model
    def create_direct_costs(self, row_values, header_indexes, revision, common_data, book):
        pass

    @api.model
    def create_total_price(self, row_values, header_indexes, revision, common_data, book):
        pass

    # Metodo para obtener la fecha en formato 'YYYY-MM-DD'
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

    # Metodo que asigna un boolean segun el valor de la celda SÍ/NO
    def get_boolean_value(self, value):
        if value == 'SÍ':
            return True
        else:
            return False
