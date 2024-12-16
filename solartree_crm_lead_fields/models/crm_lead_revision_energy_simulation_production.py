from odoo import fields, models, api


class CrmLeadRevisionEnergySimulationProduction(models.Model):
    _name = "crm.lead.revision.energy.simulation.production"
    _description = "Lead Revision Energy Simulation Production"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )

    type_energy_simulation_production_id = fields.Many2one(
        "crm.lead.revision.global.type",
        string="Type",
        domain=lambda self: self._domain_type_energy_simulation_production_id(),
    )

    selected_type_energy_simulation_production_ids = fields.Many2many(
        'crm.lead.revision.global.type',
        compute='_compute_selected_type_energy_simulation_production_ids',
        store=False
    )

    @api.depends('revision_id.revision_energy_simulation_production_ids.type_energy_simulation_production_id')
    def _compute_selected_type_energy_simulation_production_ids(self):
        for record in self:
            record.selected_type_energy_simulation_production_ids = record.mapped(
                'revision_id.revision_energy_simulation_production_ids.type_energy_simulation_production_id')

    def _domain_type_energy_simulation_production_id(self):
        return [('id', 'not in', self.selected_type_energy_simulation_production_ids.ids),
                ('behavior', '=', 'energy_simulation'),
                ('behavior_extra', '=', 'production')
                ]

    ########################################

    total = fields.Integer(
        string="Total",
        store=True,
    )

    total_calculation = fields.Integer(
        string="Total Calculation",
        compute='_compute_total_calculation',
        store=True,
    )

    @api.depends('revision_id.revision_energy_simulation_production_ids', 'revision_id.solartree_lead_modality_id')
    def _compute_total_calculation(self):
        for record in self:
            if record.type_energy_simulation_production_id.name == "Excedentes (Prod.)":
                if record.revision_id.solartree_lead_modality_id.name == 'AUTOCONSUMO SIN VERTIDO':
                    record.total_calculation = 0
                else:
                    # recorre la tabla de este modelo con este revision id hazlo aqui debajo
                    autoconsumo_prod = self._get_autoconsumo_prod(
                        record.revision_id.revision_energy_simulation_production_ids)
                    produccion = self._get_produccion(record.revision_id.revision_energy_simulation_production_ids)
                    record.total_calculation = produccion - autoconsumo_prod
                    print(
                        f"Producción: {produccion}, Autoconsumo (Prod.): {autoconsumo_prod}, Excedentes Total: {record.total_calculation}")

    kwh_per_year = fields.Integer(
        string="kWh/año",
        compute='_compute_kwh_per_year',
        store=True,
    )

    @api.depends('total', 'total_calculation')
    def _compute_kwh_per_year(self):
        for record in self:
            if record.percentage:
                record.kwh_per_year = record.total + record.total_calculation

    percentage = fields.Float(
        string="Percentage",
        compute='_compute_percentage',
        store=True,
    )

    @api.depends('revision_id.revision_energy_simulation_production_ids')
    def _compute_percentage(self):
        for record in self:
            if record.total or record.total_calculation:
                if record.type_energy_simulation_production_id.name == "Autoconsumo (Prod.)":
                    produccion = self._get_produccion(record.revision_id.revision_energy_simulation_production_ids)
                    autoconsumo = self._get_autoconsumo_prod(
                        record.revision_id.revision_energy_simulation_production_ids)

                    if produccion:
                        record.percentage = autoconsumo / produccion
                    else:
                        record.percentage = 0
                elif record.type_energy_simulation_production_id.name == "Excedentes (Prod.)":
                    produccion = self._get_produccion(record.revision_id.revision_energy_simulation_production_ids)
                    exced = self._get_exced_prod(record.revision_id.revision_energy_simulation_production_ids)
                    print(f"Producción: {produccion}, Excedentes: {exced}")
                    if produccion:
                        record.percentage = exced / produccion
                        print(f"Porcentaje de excedentes: {record.percentage}")
                    else:
                        record.percentage = 0
                else:
                    record.percentage = 0
            else:
                record.percentage = 0

    def _get_autoconsumo_prod(self, revision_energy_simulation_production_ids):
        for sim in revision_energy_simulation_production_ids:
            if sim.type_energy_simulation_production_id.name == "Autoconsumo (Prod.)":
                return sim.total
        return 0

    def _get_exced_prod(self, revision_energy_simulation_production_ids):
        for sim in revision_energy_simulation_production_ids:
            if sim.type_energy_simulation_production_id.name == "Excedentes (Prod.)":
                return sim.total_calculation
        return 0

    def _get_produccion(self, revision_energy_simulation_production_ids):
        for sim in revision_energy_simulation_production_ids:
            if sim.type_energy_simulation_production_id.name == "Producción":
                return sim.total
        return 0

    is_excedentes_prod = fields.Boolean(
        string="Is Excedentes (Prod.) or Red (Dem.)",
        compute='_compute_is_excedentes_prod',
        store=True
    )
    is_produccion_or_autoconsumo = fields.Boolean(
        string="Is Producción or Autoconsumo (Prod.)",
        compute='_compute_is_produccion_or_autoconsumo',
        store=True
    )
    is_produccion = fields.Boolean(
        string="Is Producción",
        compute='_compute_is_produccion',
        store=True
    )

    @api.depends('type_energy_simulation_production_id.name')
    def _compute_is_excedentes_prod(self):
        for record in self:
            record.is_excedentes_prod = record.type_energy_simulation_production_id.name in ['Excedentes (Prod.)']

    @api.depends('type_energy_simulation_production_id.name')
    def _compute_is_produccion_or_autoconsumo(self):
        for record in self:
            record.is_produccion_or_autoconsumo = record.type_energy_simulation_production_id.name in ['Producción',
                                                                                                       'Autoconsumo (Prod.)',
                                                                                                       ]

    @api.depends('type_energy_simulation_production_id.name')
    def _compute_is_produccion(self):
        for record in self:
            record.is_produccion = record.type_energy_simulation_production_id.name in ['Producción']
