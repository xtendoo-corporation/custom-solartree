from odoo import fields, models, api


class CrmLeadRevisionEnergySimulation(models.Model):
    _name = "crm.lead.revision.energy.simulation"
    _description = "Lead Revision Energy Simulation"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )

    type_energy_simulation_id = fields.Many2one(
        "crm.lead.revision.global.type",
        string="Type",
        domain=lambda self: self._domain_type_energy_simulation_id(),
    )

    selected_type_energy_simulation_ids = fields.Many2many(
        'crm.lead.revision.global.type',
        compute='_compute_selected_type_energy_simulation_ids',
        store=False
    )

    @api.depends('revision_id.revision_energy_simulation_ids.type_energy_simulation_id')
    def _compute_selected_type_energy_simulation_ids(self):
        for record in self:
            record.selected_type_energy_simulation_ids = record.mapped('revision_id.revision_energy_simulation_ids.type_energy_simulation_id')

    def _domain_type_energy_simulation_id(self):
        return [('id', 'not in', self.selected_type_energy_simulation_ids.ids),
                ('behavior', '=', 'energy_simulation')
                ]

    total = fields.Integer(
        string="Total",
        compute='_compute_total',
        store=True,
    )

    @api.depends('revision_id.revision_energy_simulation_ids', 'revision_id.solartree_lead_modality_id',
                 'revision_id.lead_id.customer_consumption_mwh')
    def _compute_total(self):
        print("HOLAAAAAAAAAAAAAAAAAAAAAA")
        # for record in self:
        #     # if record.type_energy_simulation_id.name == "Excedentes (Prod.)":
        #     #     if record.revision_id.solartree_lead_modality_id.name == 'AUTOCONSUMO SIN VERTIDO':
        #     #         record.total = 0
        #     #     else:
        #     #         # recorre la tabla de este modelo con este revision id hazlo aqui debajo
        #     #         autoconsumo_prod = self._get_autoconsumo_prod(record.revision_id.revision_energy_simulation_ids)
        #     #         produccion = self._get_produccion(record.revision_id.revision_energy_simulation_ids)
        #     #         record.total = produccion - autoconsumo_prod
        #     #         print(f"Producción: {produccion}, Autoconsumo (Prod.): {autoconsumo_prod}, Excedentes Total: {record.total}")
        #     if record.type_energy_simulation_id.name == "Demanda":
        #         record.total = record.revision_id.lead_id.customer_consumption_mwh
        #     elif record.type_energy_simulation_id.name == "Red (Dem.)":
        #         if record.revision_id.lead_id and record.revision_id.lead_id.customer_consumption_mwh:
        #             autoconsumo_prod = self._get_autoconsumo_prod(record.revision_id.revision_energy_simulation_ids)
        #
        #             record.total = record.revision_id.lead_id.customer_consumption_mwh - autoconsumo_prod
        #         else:
        #             record.total = 0
        #     else:
        #         record.total = 0

    total_calculation = fields.Integer(
        string="Total Calculation",
        compute='_compute_total_calculation',
        store=True,
    )

    @api.depends('revision_id.revision_energy_simulation_ids', 'revision_id.solartree_lead_modality_id',
                    'revision_id.lead_id.customer_consumption_mwh')
    def _compute_total_calculation(self):
        for record in self:
            if record.type_energy_simulation_id.name == "Excedentes (Prod.)":
                if record.revision_id.solartree_lead_modality_id.name == 'AUTOCONSUMO SIN VERTIDO':
                    record.total_calculation = 0
                else:
                    # recorre la tabla de este modelo con este revision id hazlo aqui debajo
                    autoconsumo_prod = self._get_autoconsumo_prod(record.revision_id.revision_energy_simulation_ids)
                    produccion = self._get_produccion(record.revision_id.revision_energy_simulation_ids)
                    record.total_calculation = produccion - autoconsumo_prod
                    print(
                        f"Producción: {produccion}, Autoconsumo (Prod.): {autoconsumo_prod}, Excedentes Total: {record.total_calculation}")
            elif record.type_energy_simulation_id.name == "Red (Dem.)":
                if record.revision_id.lead_id and record.revision_id.lead_id.customer_consumption_mwh:
                    autoconsumo_dem = self._get_autoconsumo_dem(record.revision_id.revision_energy_simulation_ids)
                    demanda = self._get_demanda(record.revision_id.revision_energy_simulation_ids)
                    record.total_calculation = demanda - autoconsumo_dem

    percentage = fields.Float(
        string="Percentage",
        compute='_compute_percentage',
        store=True,
    )

    @api.depends('revision_id.revision_energy_simulation_ids',
                 'revision_id.lead_id.customer_consumption_mwh')
    def _compute_percentage(self):
        print("EYYYYYYYYYYYYYYYYYYY")
        for record in self:
            if record.total or record.total_calculation:
                if record.type_energy_simulation_id.name == "Autoconsumo (Prod.)":
                    produccion = self._get_produccion(record.revision_id.revision_energy_simulation_ids)
                    autoconsumo = self._get_autoconsumo_prod(record.revision_id.revision_energy_simulation_ids)

                    if produccion:
                        record.percentage = autoconsumo / produccion
                    else:
                        record.percentage = 0
                elif record.type_energy_simulation_id.name == "Excedentes (Prod.)":
                    produccion = self._get_produccion(record.revision_id.revision_energy_simulation_ids)
                    autoconsumo = self._get_autoconsumo_prod(record.revision_id.revision_energy_simulation_ids)
                    print(f"Producción: {produccion}, Autoconsumo (Prod.): {autoconsumo}")
                    if produccion:
                        record.percentage = 100 / (produccion - autoconsumo)
                        print(f"Porcentaje: {record.percentage}")
                    else:
                        record.percentage = 0
                elif record.type_energy_simulation_id.name == "Autoconsumo (Dem.)":
                    if record.revision_id.lead_id and record.revision_id.lead_id.customer_consumption_mwh:
                        autoconsumo = self._get_autoconsumo_dem(record.revision_id.revision_energy_simulation_ids)
                        demanda = self._get_demanda(record.revision_id.revision_energy_simulation_ids)
                        record.percentage = autoconsumo / demanda
                    else:
                        record.percentage = 0
                elif record.type_energy_simulation_id.name == "Red (Dem.)":
                    if record.revision_id.lead_id and record.revision_id.lead_id.customer_consumption_mwh:
                        demanda = self._get_demanda(record.revision_id.revision_energy_simulation_ids)
                        red = self._get_red_dem(record.revision_id.revision_energy_simulation_ids)
                        record.percentage = red / demanda
                    else:
                        record.percentage = 0
                else:
                    record.percentage = 0
            else:
                record.percentage = 0


    def _get_autoconsumo_prod(self, revision_energy_simulation_ids):
        for sim in revision_energy_simulation_ids:
            if sim.type_energy_simulation_id.name == "Autoconsumo (Prod.)":
                return sim.total
        return 0

    def _get_exced_prod(self, revision_energy_simulation_ids):
        for sim in revision_energy_simulation_ids:
            if sim.type_energy_simulation_id.name == "Excendentes (Prod.)":
                return sim.total_calculation
        return 0

    def _get_autoconsumo_dem(self, revision_energy_simulation_ids):
        for sim in revision_energy_simulation_ids:
            if sim.type_energy_simulation_id.name == "Autoconsumo (Dem.)":
                return sim.total
        return 0

    def _get_red_dem(self, revision_energy_simulation_ids):
        for sim in revision_energy_simulation_ids:
            if sim.type_energy_simulation_id.name == "Red (Dem.)":
                return sim.total_calculation
        return 0

    def _get_produccion(self, revision_energy_simulation_ids):
        for sim in revision_energy_simulation_ids:
            if sim.type_energy_simulation_id.name == "Producción":
                return sim.total
        return 0

    def _get_demanda(self, revision_energy_simulation_ids):
        for sim in revision_energy_simulation_ids:
            if sim.type_energy_simulation_id.name == "Demanda":
                return sim.total
        return 0

