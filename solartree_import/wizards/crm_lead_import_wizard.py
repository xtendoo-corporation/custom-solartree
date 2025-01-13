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

            if not crm_lead_data:
                break

            # print("*" * 100)
            # print(f"Creando lead con datos: {crm_lead_data}")

            crm_lead_record = self.env['crm.lead'].create(crm_lead_data)
            self.change_stage(crm_lead_record, row_values[header_indexes['Etapa']])

            # Procesar revisiones
            for revision in revision_columns:
                revision_data = {}  # Inicializar datos para la revisión actual

                # Recopilar campos de la revisión actual basados en su prefijo
                for header in headers:
                    if header.startswith(revision + '-'):
                        column_name = header[len(revision) + 1:]  # Eliminar el prefijo de revisión
                        # print("*" * 100)
                        # print(f"Column name: {column_name}")
                        value = row_values[header_indexes[header]]
                        # print(f"Value: {value}")
                        if value:
                            revision_data[column_name] = value

                # Verificar si hay datos válidos para esta revisión antes de crearla
                if revision_data:
                    # print(f"Creando revisión para {revision} con datos: {revision_data}")
                    revision_record_data = self.create_revision(row_values, header_indexes, revision, book)
                    revision_record = self.env['crm.lead.revision'].with_context(
                        default_lead_id=crm_lead_record.id).create(revision_record_data)

                    # Crear el resto de los registros relacionados con la revisión
                    self.create_fee_and_margins(row_values, header_indexes, revision, revision_record)
                    self.create_energy_simulation_production(row_values, header_indexes, revision, revision_record)
                    self.create_direct_costs_price_cost(row_values, header_indexes, revision, revision_record)
                    self.create_direct_costs_price_sale(row_values, header_indexes, revision, revision_record)
                    self.create_inversor(row_values, header_indexes, revision, revision_record)
                    self.create_energy_simulation_demand(row_values, header_indexes, revision, revision_record)
                    self.create_battery(row_values, header_indexes, revision, revision_record)
                    prefix = revision.split('-')[0]
                    revision_record.write({
                        'installation_cost_price': row_values[header_indexes[f'{prefix}-Coste de Instalación (€)']],
                        'installation_sale_price': row_values[header_indexes[f'Oferta_Precio-{prefix}']]
                    })
                else:
                    print(
                        f"No se encontraron datos válidos para la revisión {revision}. Datos encontrados: {revision_data}")

            selected_revision_name = row_values[header_indexes['Revisión Seleccionada']]
            print("Prueba 1: ", selected_revision_name)
            selected_revision_id = self.get_selected_revision(crm_lead_record, selected_revision_name)
            print("Prueba 2: ", selected_revision_id)
            print("Prueba 3: ", selected_revision_id.id)
            if selected_revision_id:
                crm_lead_record.write({'selected_revision_id': selected_revision_id.id})
                selected_revision_id.write({'offer_selected': True})
                self.env.cr.flush()
                selected_revision_id._onchange_offer_selected()  # Explicitly call the onchange method
                crm_lead_record._onchange_selected_revision_id()
                print("@" * 100)
                print(f"Revisión seleccionada: {selected_revision_id.name}")
                print(f"Revisión seleccionada offer_selected: {selected_revision_id.offer_selected}")
            else:
                print(f"No se encontró la revisión seleccionada: {selected_revision_name}")

        # Limpiar la sesión de base de datos
        self.env.cr.flush()

    @api.model
    def create_crm_lead(self, row_values, header_indexes, book):
        try:
            value = row_values[header_indexes['Nº Proyecto']]
            if value:
                solartree_num_proyect = int(value)
            else:
                solartree_num_proyect = None
        except (ValueError, KeyError):
            solartree_num_proyect = None

        solartree_code = row_values[header_indexes['Código Oferta']]
        if not solartree_code:
            return None

        crm_lead_data = {
            'type': 'opportunity',
            'solartree_code': solartree_code,
            'user_id': self.get_user_by_dni(row_values[header_indexes['Comercial']]).id,
            'partner_id': self.get_partner_by_dni(row_values[header_indexes['Cliente']]).id,
            'name': row_values[header_indexes['Nombre de la oferta']],
            'solartree_lead_channel': self.get_or_create_record('crm.lead.channel',
                                                                row_values[header_indexes['Oferta Canal']]).id,
            'solartree_cups': row_values[header_indexes['CUPS']],
            'solartree_date_proposed_signature': self.get_date_formatted(
                row_values[header_indexes['Fecha Firma propuesta']],
                book),
            'solartree_date_kom': self.get_date_formatted(row_values[header_indexes['Fecha KOM']], book),
            'solartree_date_visit': self.get_date_formatted(row_values[header_indexes['Fecha Visita']], book),
            'solartree_date_deliverables': self.get_date_formatted(row_values[header_indexes['Fecha Entregables']],
                                                                   book),
            'solartree_date_sign_contract': self.get_date_formatted(row_values[header_indexes['Fecha Firma Contrato']],
                                                                    book),
            'solartree_num_proyect': solartree_num_proyect,
            'solartree_date_request': self.get_date_formatted(
                row_values[header_indexes['Fecha de Solicitud de Oferta']], book),
            'selected_revision_id': None,
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
            'offer_ve_kwn': row_values[header_indexes[f'{prefix}-Oferta VE kWn']],
            'offer_tot': self.get_user_by_dni(row_values[header_indexes[f'{prefix}-Técnico OT']]).id,
            'offer_HT': row_values[header_indexes[f'{prefix}-HT Oferta']],
            'offer_pb_actual': row_values[header_indexes[f'{prefix}-PB actuales']],
            'offer_pb_omip': row_values[header_indexes[f'{prefix}-PB OMIP']],
            'offer_pb_proyection': row_values[header_indexes[f'{prefix}-PB proyección']],
            'offer_tir_actual': row_values[header_indexes[f'{prefix}-TIR actuales %']] * 100,
            'offer_tir_omip': row_values[header_indexes[f'{prefix}-TIR OMIP %']] * 100,
            'offer_tir_proyection': row_values[header_indexes[f'{prefix}-TIR proyección %']] * 100,
            'offer_date_deliver': self.get_date_formatted(row_values[header_indexes[f'{prefix}-Fecha Entrega Oferta']],
                                    book),
        }
        return revision_data

    @api.model
    def create_fee_and_margins(self, row_values, header_indexes, revision, revision_record):
        fee_types = [
            ('Fee Interno', '-Fee Interno'),
            ('Fee Externo', '-Fee Externo'),
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
            if isinstance(row_values[header_indexes[f'{revision}{fee_column}']], (int, float)):
                fee_value = row_values[header_indexes[f'{revision}{fee_column}']]
            else:
                fee_value = 0

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
            # ('Autoconsumo (Prod.)', '-Autoconsumo (Prod.)'),
            # ('Excedentes (Prod.)', '-Excedentes (Prod.)'),
        ]

        for production_name, production_column in energy_simulation_production_types:
            # Buscar el registro de tipo de precio
            type_production = self.env['crm.lead.revision.global.type'].search([('name', '=', production_name)],
                                                                               limit=1)

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

    # WIP
    @api.model
    def create_energy_simulation_demand(self, row_values, header_indexes, revision, revision_record):
        energy_simulation_demand_types = [
            ('Demanda', 'Consumo del cliente (kWh/año)'),
            # ('Autoconsumo (Dem.)', f'{revision}-Autoconsumo (Prod.)'),
            # ('Red (Dem.)', f'{revision}-Red (Dem.)'),
        ]

        for demand_name, demand_column in energy_simulation_demand_types:
            # Buscar el registro de tipo de precio
            type_demand = self.env['crm.lead.revision.global.type'].search([('name', '=', demand_name)], limit=1)

            # Si no existe, crear el tipo de precio con el comportamiento especificado
            if not type_demand:
                type_demand = self.env['crm.lead.revision.global.type'].create({
                    'name': demand_name,
                    'behavior': 'demand',
                })

            existing_demand = self.env['crm.lead.revision.energy.simulation.demand'].search([
                ('revision_id', '=', revision_record.id),
                ('type_energy_simulation_demand_id', '=', type_demand.id)
            ], limit=1)

            # if existing_demand:
            #     existing_demand.write({
            #         'total': row_values[header_indexes[demand_column]]
            #     })
            # else:
            #     # Crear el registro de precios con el porcentaje para cada revisión
            #     demand_data = {
            #         'revision_id': revision_record.id,  # Usar el ID de la revisión creada
            #         'type_energy_simulation_demand_id': type_demand.id,
            #         'total': row_values[header_indexes[demand_column]]
            #     }
            #     # Crear el registro de precios en la base de datos
            #     self.env['crm.lead.revision.energy.simulation.demand'].create(demand_data)

    # Metodo para construir los datos de inversor
    @api.model
    def create_inversor(self, row_values, header_indexes, revision, revision_record):
        inverter_index = 0
        while f'{revision}-revision_inverter_model_{inverter_index}' in header_indexes:
            model = row_values[header_indexes[f'{revision}-revision_inverter_model_{inverter_index}']]
            power = row_values[header_indexes[f'{revision}-revision_inverter_power_{inverter_index}']]
            quantity = row_values[header_indexes[f'{revision}-revision_inverter_quantity_{inverter_index}']]

            if model or power or quantity:
                inverter_data = {
                    'revision_id': revision_record.id,
                    'offer_inverter_model': model,
                    'offer_inverter_unit_power': power,
                    'offer_inverter_quantity': quantity,
                }
                self.env['crm.lead.revision.inverter'].create(inverter_data)

            inverter_index += 1

    @api.model
    def create_battery(self, row_values, header_indexes, revision, revision_record):
        battery_index = 0
        while f'{revision}-revision_battery_model_{battery_index}' in header_indexes:
            model = row_values[header_indexes[f'{revision}-revision_battery_model_{battery_index}']]
            capacity = row_values[header_indexes[f'{revision}-revision_battery_capacity_{battery_index}']]
            power = row_values[header_indexes[f'{revision}-revision_battery_power_{battery_index}']]
            quantity = row_values[header_indexes[f'{revision}-revision_battery_quantity_{battery_index}']]

            if model or capacity or power or quantity:
                battery_data = {
                    'revision_id': revision_record.id,
                    'offer_battery_model': model,
                    'offer_battery_capacity': capacity,
                    'offer_battery_power': power,
                    'offer_battery_quantity': quantity,
                }
                self.env['crm.lead.revision.battery'].create(battery_data)

            battery_index += 1

    @api.model
    def create_direct_costs_price_cost(self, row_values, header_indexes, revision, revision_record):
        # Definir los tipos de precio a procesar
        cost_types = [
            ('Modulos', '-revision_direct_costs_ids_Modulos_Coste'),
            ('Inversor', '-revision_direct_costs_ids_Inversor_Coste'),
            ('Batería', '-revision_direct_costs_ids_Batería_Coste'),
            ('Estructura', '-revision_direct_costs_ids_Estructura_Coste'),
            ('Evacuación', '-revision_direct_costs_ids_Evacuación_Coste'),
            ('H&S', '-revision_direct_costs_ids_H&S_Coste'),
            ('BOP', '-revision_direct_costs_ids_BOP_Coste'),
            ('Ingeniería', '-revision_direct_costs_ids_Ingeniería_Coste'),
            ('Vehículo Eléctrico (VE)', '-revision_direct_costs_ids_Vehículo Eléctrico (VE)_Coste'),
            ('Staff y Servicios de Obra', '-revision_direct_costs_ids_Staff y Servicios de Obra_Coste'),
            ('Operación y Mantenimiento', '-revision_direct_costs_ids_Operación y Mantenimiento_Coste'),
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

            existing_cost = self.env['crm.lead.revision.direct.costs'].search([
                ('revision_id', '=', revision_record.id),
                ('type_direct_costs_id', '=', type_cost.id)
            ], limit=1)

            # if existing_cost:
            #     existing_cost.write({
            #         'price_cost': row_values[header_indexes[f'{revision}{cost_column}']]
            #     })
            # else:
            #     # Crear el registro de precios con el porcentaje para cada revisión
            #     cost_data = {
            #         'revision_id': revision_record.id,  # Usar el ID de la revisión creada
            #         'type_direct_costs_id': type_cost.id,
            #         'price_cost': row_values[header_indexes[f'{revision}{cost_column}']]
            #     }
            #     # Crear el registro de precios en la base de datos
            #     self.env['crm.lead.revision.direct.costs'].create(cost_data)

    @api.model
    def create_direct_costs_price_sale(self, row_values, header_indexes, revision, revision_record):
        # Definir los tipos de precio a procesar
        cost_types = [
            ('Modulos', '-revision_direct_costs_ids_Modulos_Venta'),
            ('Inversor', '-revision_direct_costs_ids_Inversor_Venta'),
            ('Batería', '-revision_direct_costs_ids_Batería_Venta'),
            ('Estructura', '-revision_direct_costs_ids_Estructura_Venta'),
            ('Evacuación', '-revision_direct_costs_ids_Evacuación_Venta'),
            ('H&S', '-revision_direct_costs_ids_H&S_Venta'),
            ('BOP', '-revision_direct_costs_ids_BOP_Venta'),
            ('Ingeniería', '-revision_direct_costs_ids_Ingeniería_Venta'),
            ('Vehículo Eléctrico (VE)', '-revision_direct_costs_ids_Vehículo Eléctrico (VE)_Venta'),
            ('Staff y Servicios de Obra', '-revision_direct_costs_ids_Staff y Servicios de Obra_Venta'),
            ('Operación y Mantenimiento', '-revision_direct_costs_ids_Operación y Mantenimiento_Venta'),
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

            existing_cost = self.env['crm.lead.revision.direct.costs'].search([
                ('revision_id', '=', revision_record.id),
                ('type_direct_costs_id', '=', type_cost.id)
            ], limit=1)

            # if existing_cost:
            #     existing_cost.write({
            #         'price_sale': row_values[header_indexes[f'{revision}{cost_column}']]
            #     })
            # else:
            #     # Crear el registro de precios con el porcentaje para cada revisión
            #     cost_data = {
            #         'revision_id': revision_record.id,  # Usar el ID de la revisión creada
            #         'type_direct_costs_id': type_cost.id,
            #         'price_sale': row_values[header_indexes[f'{revision}{cost_column}']]
            #     }
            #     # Crear el registro de precios en la base de datos
            #     self.env['crm.lead.revision.direct.costs'].create(cost_data)

    # Metodo para obtener la fecha en formato 'YYYY-MM-DD'
    def get_date_formatted(self, date_value, book):
        if isinstance(date_value, str):  # Verifica si es un string
            if date_value == '' or date_value == 'PDT':
                return None
            else:
                return date_value
        if isinstance(date_value, float):  # Verifica si es un float (el formato típico de fecha en Excel)
            # Convierte el número en una fecha usando xlrd.xldate_as_datetime
            date_as_datetime = xlrd.xldate_as_datetime(date_value, book.datemode)
            return date_as_datetime.strftime('%Y-%m-%d')

    # Metodo para obtener o crear un registro en un modelo
    @api.model
    def get_or_create_record(self, model_name, name):
        # Buscar el registro en el modelo especificado
        record = self.env[model_name].search([('name', '=', name)], limit=1)
        # if not record:
        #     # Si no existe, crear un nuevo registro
        #     record = self.env[model_name].create({'name': name})
        return record

    # Metodo que asigna un boolean segun el valor de la celda SÍ/NO
    def get_boolean_value(self, value):
        return value == 'SI'

    # Metodo obtener un usuario de odoo a partir de su dni
    def get_user_by_dni(self, dni):
        user = self.env['res.users'].search([('vat', '=', dni)], limit=1)
        return user

    def get_partner_by_dni(self, dni):
        partner = self.env['res.partner'].search([('vat', '=', dni)], limit=1)
        return partner

    def change_stage(self, crm_lead_record, stage_name):
        stage = self.env['crm.stage'].search([('name', '=', stage_name)], limit=1)
        crm_lead_record.stage_id = stage.id
        return crm_lead_record

    def get_selected_revision(self, crm_lead_record, selected_revision):
        # Revisión Seleccionada
        selected_revision_id = self.env['crm.lead.revision'].search([
            ('name', '=', selected_revision),
            ('lead_id', '=', crm_lead_record.id)
        ], limit=1)
        if selected_revision_id:
            selected_revision_id.offer_selected = True
        return selected_revision_id
