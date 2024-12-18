from odoo import models, fields, api
from odoo.exceptions import UserError
import re
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
        # Extraer solo prefijos únicos (R0, R1, ...)
        revision_columns = list(
            set(re.match(r'^(R\d+)-', header).group(1) for header in headers if re.match(r'^(R\d+)-', header)))
        # Ordenar los prefijos extraídos
        revision_columns.sort()

        for row in range(1, sheet.nrows):
            row_values = sheet.row_values(row)

            # Crear el lead principal
            crm_lead_data = self.create_crm_lead(row_values, header_indexes, book)
            crm_lead_record = self.env['crm.lead'].create(crm_lead_data)

            # Procesar revisiones
            for revision in revision_columns:
                revision_data = {}  # Inicializar datos para la revisión actual

                # Recopilar campos de la revisión actual basados en su prefijo
                for header in headers:
                    if header.startswith(revision + '-'):
                        column_name = header[len(revision) + 1:]  # Eliminar el prefijo de revisión
                        value = row_values[header_indexes[header]]
                        if value:
                            revision_data[column_name] = value

                # Verificar si hay datos válidos para esta revisión antes de crearla
                if revision_data:
                    print(f"Creando revisión para {revision} con datos: {revision_data}")
                    revision_record_data = self.create_revision(row_values, header_indexes, revision, book)
                    revision_record = self.env['crm.lead.revision'].with_context(
                        default_lead_id=crm_lead_record.id).create(revision_record_data)

                    # Procesar los costos y márgenes relacionados con esta revisión
                    self.create_fee_and_margins(row_values, header_indexes, revision, revision_record)
                    self.create_energy_simulation_production(row_values, header_indexes, revision, revision_record)
                    self.create_direct_costs_price_cost(row_values, header_indexes, revision, revision_record)
                    self.create_direct_costs_price_sale(row_values, header_indexes, revision, revision_record)

                    # self.create_direct_costs(row_values, header_indexes, revision, revision_record)

        # Limpiar la sesión de base de datos
        self.env.cr.flush()

    @api.model
    def create_crm_lead(self, row_values, header_indexes, book):
        crm_lead_data = {
            'type': 'opportunity',
            'user_id': self.get_user_by_dni(row_values[header_indexes['Comercial']]).id,
            'solartree_code': row_values[header_indexes['Código Oferta']],
            'name': row_values[header_indexes['Nombre de la oferta']],
            'solartree_lead_channel': self.get_or_create_record('crm.lead.channel',
                                                                row_values[header_indexes['Oferta Canal']]).id,
            'solartree_cups': row_values[header_indexes['CUPS']],
            'solartree_date_required_delivery': self.get_date_formatted(
                row_values[header_indexes['Fecha de entrega requerida']],
                book),
            'solartree_date_proposed_signature': self.get_date_formatted(
                row_values[header_indexes['Fecha Firma propuesta']],
                book),
            'solartree_date_kom': self.get_date_formatted(row_values[header_indexes['Fecha KOM']], book),
            'solartree_date_visit': self.get_date_formatted(row_values[header_indexes['Fecha Visita']], book),
            'solartree_date_visit_tecnic': self.get_date_formatted(
                row_values[header_indexes['Fecha informe Visita Técnica']], book),
            'solartree_date_deliverables': self.get_date_formatted(row_values[header_indexes['Fecha Entregables']],
                                                                   book),
            'solartree_date_sign_contract': self.get_date_formatted(row_values[header_indexes['Fecha Firma Contrato']],
                                                                    book),
            'solartree_num_proyect': row_values[header_indexes['Nº Proyecto']],
        }
        return crm_lead_data

    # Metodo para construir y devolver los datos de revisión
    def create_revision(self, row_values, header_indexes, revision, book):
        prefix = revision.split('-')[0]  # Obtener el prefijo (e.g., "R0")
        revision_data = {
            'solartree_lead_type_id': self.get_or_create_record('crm.lead.type',
                                                                row_values[header_indexes[f'{prefix}-Oferta Tipo']]).id,
            'solartree_lead_modality_id': self.get_or_create_record('crm.lead.modality',
                                                                    row_values[header_indexes[
                                                                        f'{prefix}-Oferta Modalidad']]).id,
            'solartree_lead_collective': self.get_boolean_value(
                row_values[header_indexes[f'{prefix}-Oferta Colectivo']]),
            'solartree_lead_storage': self.get_boolean_value(
                row_values[header_indexes[f'{prefix}-Oferta Almacenamiento']]),
            'solartree_lead_scope': self.get_or_create_record('crm.lead.scope',
                                                              row_values[
                                                                  header_indexes[f'{prefix}-Oferta Alcance']]).id,
            'solartree_lead_structure_type': self.get_or_create_record('crm.lead.structure.type',
                                                                       row_values[header_indexes[
                                                                           f'{prefix}-Oferta Estructura Tipo']]).id,
            'solartree_lead_structure_model': self.get_or_create_record('crm.lead.structure.model',
                                                                        row_values[header_indexes[
                                                                            f'{prefix}-Oferta Estructura Modelo']]).id,
            'offer_kwp': row_values[header_indexes[f'{prefix}-Oferta kWp']],
            'offer_kwn': row_values[header_indexes[f'{prefix}-Oferta kWn']],
            'offer_fabricant_modules': row_values[header_indexes[f'{prefix}-Módulos Fabricante']],
            'offer_modules_model': row_values[header_indexes[f'{prefix}-Modelo Módulos']],
            'offer_pb_actual': row_values[header_indexes[f'{prefix}-PB actuales']],
        }
        return revision_data

    @api.model
    def create_fee_and_margins(self, row_values, header_indexes, revision, revision_record):
        fee_types = [
            ('Fee Interno', '-Fee Externo'),
            ('Fee Externo', '-Fee Interno'),
            ('Beneficio Industrial', '-Beneficio Industrial'),
            ('Gastos de estructura', '-Gastos de estructura')
        ]
        # Iterar sobre los tipos de precio
        for fee_name, fee_column in fee_types:
            # Buscar el registro de tipo de precio
            type_fee = self.env['crm.lead.revision.global.type'].search([('name', '=', fee_name)], limit=1)

            # Si no existe, crear el tipo de precio con el comportamiento especificado
            if not type_fee:
                type_fee = self.env['crm.lead.revision.global.type'].create({
                    'name': fee_name,
                    'behavior': 'fee_and_margins',
                })

            # Buscar si ya existe un registro de precios para la revisión y el tipo de precio
            existing_fee = self.env['crm.lead.revision.prices'].search([
                ('revision_id', '=', revision_record.id),
                ('type_price_id', '=', type_fee.id)
            ], limit=1)

            # Obtener el valor de la celda
            fee_value = row_values[header_indexes[f'{revision}{fee_column}']]

            # Verificar si el valor es mayor que 1 (es decir, un porcentaje mal interpretado) y ajustarlo
            if fee_value > 1:
                fee_value = fee_value / 100  # Ajustar si el valor es mayor a 1 (para porcentajes)

            # Si existe, actualizarlo
            if existing_fee:
                existing_fee.write({
                    'percentage': fee_value
                })
            else:
                # Si no existe, crear un nuevo registro de precio
                fee_data = {
                    'revision_id': revision_record.id,  # Usar el ID de la revisión creada
                    'type_price_id': type_fee.id,
                    'percentage': fee_value
                }
                self.env['crm.lead.revision.prices'].create(fee_data)

    @api.model
    def create_energy_simulation_production(self, row_values, header_indexes, revision, revision_record):
        energy_simulation_production_types = [
            ('Producción', '-Producción'),
            ('Autoconsumo (Prod.)', '-Autoconsumo (Prod.)'),
            # ('Excedentes (Prod.)', '-Excedentes (Prod.)'),
        ]

        for production_name, production_column in energy_simulation_production_types:
            # Buscar el registro de tipo de precio
            type_production = self.env['crm.lead.revision.global.type'].search([('name', '=', production_name)], limit=1)

            # Si no existe, crear el tipo de precio con el comportamiento especificado
            if not type_production:
                type_production = self.env['crm.lead.revision.global.type'].create({
                    'name': production_name,
                    'behavior': 'production',
                })

            existing_production = self.env['crm.lead.revision.energy.simulation.production'].search([
                ('revision_id', '=', revision_record.id),
                ('type_energy_simulation_production_id', '=', type_production.id)
            ], limit=1)

            if existing_production:
                existing_production.write({
                    'total': row_values[header_indexes[f'{revision}{production_column}']]
                })
            else:
                # Crear el registro de precios con el porcentaje para cada revisión
                production_data = {
                    'revision_id': revision_record.id,  # Usar el ID de la revisión creada
                    'type_energy_simulation_production_id': type_production.id,
                    'total': row_values[header_indexes[f'{revision}{production_column}']]
                }
                # Crear el registro de precios en la base de datos
                self.env['crm.lead.revision.energy.simulation.production'].create(production_data)

    def create_energy_simulation_demand(self, row_values, header_indexes, revision, revision_record):
        energy_simulation_demand_types = [
            ('Demanda', 'Demanda'),
            ('Autoconsumo (Dem.)', 'Autoconsumo (Dem.)'),
            ('Red (Dem.)', 'Red (Dem.)'),
        ]


    # Metodo para construir los datos de inversor
    @api.model
    def create_inversor(self, row_values, header_indexes, revision, common_data, book):
        pass

    @api.model
    def create_battery(self, row_values, header_indexes, revision, common_data, book):
        pass

    @api.model
    def create_direct_costs_price_cost(self, row_values, header_indexes, revision, revision_record):
        # Definir los tipos de precio a procesar
        cost_types = [
            ('Modulos', '-revision_direct_costs_ids_Modulos_Coste'),
            # ('Inversor', 'Inversor'),
            # ('Batería', 'Batería'),
            # ('Estructura', 'Estructura'),
            # ('Evacuación', 'Evacuación'),
            # ('H&amp;S', 'H&amp;S'),
            # ('BOP', 'BOP'),
            # ('Ingeniería', 'Ingeniería'),
            # ('Vehículo Eléctrico (VE)', 'Vehículo Eléctrico (VE)'),
            # ('Staff y Servicios de Obra', 'Staff y Servicios de Obra'),
            # ('Operación y Mantenimiento', 'Operación y Mantenimiento'),
        ]

        # Iterar sobre los tipos de precio
        for cost_name, cost_column in cost_types:
            # Buscar el registro de tipo de precio
            type_cost = self.env['crm.lead.revision.global.type'].search([('name', '=', cost_name)], limit=1)

            # Si no existe, crear el tipo de precio con el comportamiento especificado
            if not type_cost:
                type_cost = self.env['crm.lead.revision.global.type'].create({
                    'name': cost_name,
                    'behavior': 'direct_costs',
                })

            # Crear el registro de precios con el porcentaje para cada revisión
            cost_data = {
                'revision_id': revision_record.id,  # Usar el ID de la revisión creada
                'type_price_id': type_cost.id,
                'percentage': row_values[header_indexes[f'{cost_column}{revision}']]
            }

            # Crear el registro de precios en la base de datos
            self.env['crm.lead.revision.prices'].create(cost_data)

    @api.model
    def create_direct_costs_price_sale(self, row_values, header_indexes, revision, revision_record):
        # Definir los tipos de precio a procesar
        cost_types = [
            ('Modulos', '-revision_direct_costs_ids_Modulos_Venta'),
            # ('Inversor', 'Inversor'),
            # ('Batería', 'Batería'),
            # ('Estructura', 'Estructura'),
            # ('Evacuación', 'Evacuación'),
            # ('H&amp;S', 'H&amp;S'),
            # ('BOP', 'BOP'),
            # ('Ingeniería', 'Ingeniería'),
            # ('Vehículo Eléctrico (VE)', 'Vehículo Eléctrico (VE)'),
            # ('Staff y Servicios de Obra', 'Staff y Servicios de Obra'),
            # ('Operación y Mantenimiento', 'Operación y Mantenimiento'),
        ]

        # Iterar sobre los tipos de precio
        for cost_name, cost_column in cost_types:
            # Buscar el registro de tipo de precio
            type_cost = self.env['crm.lead.revision.global.type'].search([('name', '=', cost_name)], limit=1)

            # Si no existe, crear el tipo de precio con el comportamiento especificado
            if not type_cost:
                type_cost = self.env['crm.lead.revision.global.type'].create({
                    'name': cost_name,
                    'behavior': 'direct_costs',
                })

            # Crear el registro de precios con el porcentaje para cada revisión
            cost_data = {
                'revision_id': revision_record.id,  # Usar el ID de la revisión creada
                'type_price_id': type_cost.id,
                'percentage': row_values[header_indexes[f'{cost_column}{revision}']]
            }

            # Crear el registro de precios en la base de datos
            self.env['crm.lead.revision.prices'].create(cost_data)

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

    # Metodo obtener un usuario de odoo a partir de su dni
    def get_user_by_dni(self, dni):
        user = self.env['res.users'].search([('vat', '=', dni)], limit=1)
        return user

    def get_partner_by_dni(self, dni):
        partner = self.env['res.partner'].search([('vat', '=', dni)], limit=1)
        return partner
