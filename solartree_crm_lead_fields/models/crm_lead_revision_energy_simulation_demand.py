from odoo import fields, models, api


class CrmLeadRevisionEnergySimulationDemand(models.Model):
    _name = "crm.lead.revision.energy.simulation.demand"
    _description = "Lead Revision Energy Simulation Demand"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )

    type_energy_simulation_demand_id = fields.Many2one(
        "crm.lead.revision.global.type",
        string="Type",
        domain=lambda self: self._domain_type_energy_simulation_demand_id(),
    )

    selected_type_energy_simulation_demand_ids = fields.Many2many(
        'crm.lead.revision.global.type',
        compute='_compute_selected_type_energy_simulation_demand_ids',
        store=False
    )

    @api.depends('revision_id.revision_energy_simulation_demand_ids.type_energy_simulation_demand_id')
    def _compute_selected_type_energy_simulation_demand_ids(self):
        for record in self:
            record.selected_type_energy_simulation_demand_ids = record.mapped(
                'revision_id.revision_energy_simulation_demand_ids.type_energy_simulation_demand_id')

    def _domain_type_energy_simulation_demand_id(self):
        return [('id', 'not in', self.selected_type_energy_simulation_demand_ids.ids),
                ('behavior', '=', 'energy_simulation'),
                ('behavior_extra', '=', 'demand')
                ]

    total = fields.Integer(
        string="Total",
        store=True,
        compute='_compute_total',
        readonly=False,
    )

    @api.depends('revision_id.lead_id.customer_consumption_mwh', 'revision_id.revision_energy_simulation_production_ids',)
    def _compute_total(self):
        for record in self:
            if record.type_energy_simulation_demand_id.name == "Demanda":
                record.total = record.revision_id.lead_id.customer_consumption_mwh
            if record.type_energy_simulation_demand_id.name == "Autoconsumo (Dem.)":
                record.total = record.revision_id.revision_energy_simulation_production_ids.filtered(
                    lambda r: r.type_energy_simulation_production_id.name == "Autoconsumo (Prod.)"
                ).total

    total_calculation = fields.Integer(
        string="Total Calculation",
        compute='_compute_total_calculation',
        store=True,
    )

    @api.depends('revision_id.revision_energy_simulation_demand_ids', 'revision_id.solartree_lead_modality_id',
                 'revision_id.lead_id.customer_consumption_mwh')
    def _compute_total_calculation(self):
        for record in self:
            if record.type_energy_simulation_demand_id.name == "Red (Dem.)":
                if record.revision_id.lead_id and record.revision_id.lead_id.customer_consumption_mwh:
                    autoconsumo_dem = self._get_autoconsumo_dem(
                        record.revision_id.revision_energy_simulation_demand_ids)
                    demanda = self._get_demanda(record.revision_id.revision_energy_simulation_demand_ids)
                    record.total_calculation = demanda - autoconsumo_dem

    percentage = fields.Float(
        string="Percentage",
        compute='_compute_percentage',
        store=True,
    )

    @api.depends('revision_id.revision_energy_simulation_demand_ids',
                 'revision_id.lead_id.customer_consumption_mwh')
    def _compute_percentage(self):
        for record in self:
            if record.total or record.total_calculation:
                if record.type_energy_simulation_demand_id.name == "Autoconsumo (Dem.)":
                    if record.revision_id.lead_id and record.revision_id.lead_id.customer_consumption_mwh:
                        autoconsumo = self._get_autoconsumo_dem(
                            record.revision_id.revision_energy_simulation_demand_ids)
                        demanda = self._get_demanda(record.revision_id.revision_energy_simulation_demand_ids)
                        record.percentage = autoconsumo / demanda
                    else:
                        record.percentage = 0
                elif record.type_energy_simulation_demand_id.name == "Red (Dem.)":
                    if record.revision_id.lead_id and record.revision_id.lead_id.customer_consumption_mwh:
                        demanda = self._get_demanda(record.revision_id.revision_energy_simulation_demand_ids)
                        red = self._get_red_dem(record.revision_id.revision_energy_simulation_demand_ids)
                        print(f"Demanda: {demanda}, Red: {red}")
                        record.percentage = red / demanda
                        print(f"Porcentaje de red: {record.percentage}")
                    else:
                        record.percentage = 0
                else:
                    record.percentage = 0
            else:
                record.percentage = 0

    def _get_autoconsumo_dem(self, revision_energy_simulation_demand_ids):
        for sim in revision_energy_simulation_demand_ids:
            if sim.type_energy_simulation_demand_id.name == "Autoconsumo (Dem.)":
                return sim.total
        return 0

    def _get_red_dem(self, revision_energy_simulation_demand_ids):
        for sim in revision_energy_simulation_demand_ids:
            if sim.type_energy_simulation_demand_id.name == "Red (Dem.)":
                return sim.total_calculation
        return 0

    def _get_demanda(self, revision_energy_simulation_demand_ids):
        for sim in revision_energy_simulation_demand_ids:
            if sim.type_energy_simulation_demand_id.name == "Demanda":
                return sim.total
        return 0

    is_red_dem = fields.Boolean(
        string="Is Red (Dem.)",
        compute='_compute_is_red_dem',
        store=True
    )
    is_autoconsumo_or_demanda = fields.Boolean(
        string="Is Demanda or Autoconsumo (Dem.)",
        compute='_compute_is_autoconsumo_or_demanda',
        store=True
    )
    is_demanda = fields.Boolean(
        string="Is Demanda",
        compute='_compute_is_demanda',
        store=True
    )

    @api.depends('type_energy_simulation_demand_id.name')
    def _compute_is_red_dem(self):
        for record in self:
            record.is_red_dem = record.type_energy_simulation_demand_id.name in ['Red (Dem.)']

    @api.depends('type_energy_simulation_demand_id.name')
    def _compute_is_autoconsumo_or_demanda(self):
        for record in self:
            record.is_autoconsumo_or_demanda = record.type_energy_simulation_demand_id.name in ['Demanda',
                                                                                                'Autoconsumo (Dem.)']

    @api.depends('type_energy_simulation_demand_id.name')
    def _compute_is_demanda(self):
        for record in self:
            record.is_demanda = record.type_energy_simulation_demand_id.name in ['Demanda']
