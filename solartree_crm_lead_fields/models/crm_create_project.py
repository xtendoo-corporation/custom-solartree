from odoo import models, fields, api

class CrmCreateProjectInherited(models.TransientModel):
    _inherit = "crm.create.project"

    @api.model
    def default_get(self, fields):
        res = super(CrmCreateProjectInherited, self).default_get(fields)
        if 'default_project_name' in self.env.context:
            print("*"*80)
            print(self.env.context)
            res['project_name'] = self.env.context['default_project_name']
        return res

    def create_project(self):
        if self.duplicate_project_id:
            project = self.duplicate_project_id.copy(
                {
                    "name": self.project_name,
                    "description": self.project_description,
                    "lead_id": self.lead_id.id,
                }
            )
        else:
            project = (
                self.env["project.project"]
                .sudo()
                .create(self._prepare_create_project_values())
            )
        self.lead_id.project_id = project

    def _prepare_create_project_values(self):
        values = {
            "name": self.project_name,
            "description": self.project_description,
            "active": True,
            "allow_billable": True,
        }
        if self.duplicate_project_id:
            values.update(
                {
                    "name": self.project_name,
                    "description": self.project_description,
                    "lead_id": self.lead_id.id,
                    "partner_id": self.lead_id.partner_id.id,
                    "company_id": self.lead_id.company_id.id,
                }
            )
        else:
            values.update(
                {
                    "partner_id": self.lead_id.partner_id.id,
                    "company_id": self.lead_id.company_id.id,
                }
            )
        return values

    def create_project(self):
        super(CrmCreateProjectInherited, self).create_project()
        project = self.lead_id.project_id

        # Añadir los datos de la revisión al proyecto recién creado
        project_revision = self.env['project.revision'].create({
            'name': self.lead_id.selected_revision_id.name,
            'project_id': project.id,
            'solartree_lead_type_id': self.lead_id.selected_revision_id.solartree_lead_type_id.id,
            'solartree_lead_scope': self.lead_id.selected_revision_id.solartree_lead_scope.id,
            'solartree_lead_modality_id': self.lead_id.selected_revision_id.solartree_lead_modality_id.id,
            'solartree_lead_collective': self.lead_id.selected_revision_id.solartree_lead_collective,
            'solartree_lead_storage': self.lead_id.selected_revision_id.solartree_lead_storage,
            'solartree_lead_structure_type': self.lead_id.selected_revision_id.solartree_lead_structure_type.id,
            'solartree_lead_structure_model': self.lead_id.selected_revision_id.solartree_lead_structure_model.id,
            'offer_kwp': self.lead_id.selected_revision_id.offer_kwp,
            'offer_kwn': self.lead_id.selected_revision_id.offer_kwn,
            'offer_storage_kwh': self.lead_id.selected_revision_id.offer_storage_kwh,
            'offer_storage_kwn': self.lead_id.selected_revision_id.offer_storage_kwn,
            'offer_ve_kwn': self.lead_id.selected_revision_id.offer_ve_kwn,
            'offer_tot': self.lead_id.selected_revision_id.offer_tot.id,
            'offer_date_deliver': self.lead_id.selected_revision_id.offer_date_deliver,
            'offer_HT': self.lead_id.selected_revision_id.offer_HT,
            'offer_pb_actual': self.lead_id.selected_revision_id.offer_pb_actual,
            'offer_tir_actual': self.lead_id.selected_revision_id.offer_tir_actual,
            'offer_pb_omip': self.lead_id.selected_revision_id.offer_pb_omip,
            'offer_tir_omip': self.lead_id.selected_revision_id.offer_tir_omip,
            'offer_pb_proyection': self.lead_id.selected_revision_id.offer_pb_proyection,
            'offer_tir_proyection': self.lead_id.selected_revision_id.offer_tir_proyection,
            'avg_price': self.lead_id.selected_revision_id.avg_price,
            'surplus_price': self.lead_id.selected_revision_id.surplus_price,
            'pb_exced_min': self.lead_id.selected_revision_id.pb_exced_min,
            'tir_exced_min': self.lead_id.selected_revision_id.tir_exced_min,
            'pb_battery': self.lead_id.selected_revision_id.pb_battery,
            'tir_battery': self.lead_id.selected_revision_id.tir_battery,
            'offer_fabricant_modules': self.lead_id.selected_revision_id.offer_fabricant_modules,
            'offer_modules_model': self.lead_id.selected_revision_id.offer_modules_model,
            'offer_modules_unit_power': self.lead_id.selected_revision_id.offer_modules_unit_power,
            'offer_modules_quantity': self.lead_id.selected_revision_id.offer_modules_quantity,
            'offer_inverter_manufacturer': self.lead_id.selected_revision_id.offer_inverter_manufacturer,
            'offer_battery_manufacturer': self.lead_id.selected_revision_id.offer_battery_manufacturer,
            'offer_structure_manufacturer': self.lead_id.selected_revision_id.offer_structure_manufacturer,
            'offer_structure_description': self.lead_id.selected_revision_id.offer_structure_description,
            'offer_class_id': self.lead_id.selected_revision_id.offer_class_id.id,
            'company_currency': self.lead_id.selected_revision_id.company_currency.id,
            'offer_evacuation': self.lead_id.selected_revision_id.offer_evacuation.id,
        })

        # Add new related records
        project_revision.write({
            'revision_inverter_ids': [(0, 0, {
                'type_inverter_id': inverter.type_inverter_id.id,
                'offer_inverter_model': inverter.offer_inverter_model,
                'offer_inverter_unit_power': inverter.offer_inverter_unit_power,
                'offer_inverter_quantity': inverter.offer_inverter_quantity,
            }) for inverter in self.lead_id.selected_revision_id.revision_inverter_ids],
            'revision_battery_ids': [(0, 0, {
                'type_battery_id': battery.type_battery_id.id,
                'offer_battery_model': battery.offer_battery_model,
                'offer_battery_capacity': battery.offer_battery_capacity,
                'offer_battery_power': battery.offer_battery_power,
                'offer_battery_quantity': battery.offer_battery_quantity,
            }) for battery in self.lead_id.selected_revision_id.revision_battery_ids],
            'revision_energy_simulation_project_production_ids': [(0, 0, {
                'type_energy_simulation_project_production_id': energy.type_energy_simulation_production_id.id,
                'total': energy.total,
                'percentage': energy.percentage,
            }) for energy in self.lead_id.selected_revision_id.revision_energy_simulation_production_ids],
            'revision_energy_simulation_project_demand_ids': [(0, 0, {
                'type_energy_simulation_project_demand_id': energy.type_energy_simulation_demand_id.id,
                'total': energy.total,
                'percentage': energy.percentage,
            }) for energy in self.lead_id.selected_revision_id.revision_energy_simulation_demand_ids],
        })

        project.write({
            'selected_revision_id': project_revision.id,
        })
