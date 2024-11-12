from odoo import fields, models, api


class CrmLeadRevisionBattery(models.Model):
    _name = "crm.lead.revision.battery"
    _description = "Lead Revision Battery"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )

    type_battery_id = fields.Many2one(
        "crm.lead.revision.global.type",
        string="Type",
        domain=lambda self: self._domain_type_battery_id(),
    )

    selected_type_battery_ids = fields.Many2many(
        'crm.lead.revision.global.type',
        compute='_compute_selected_type_battery_ids',
        store=False
    )

    @api.depends('revision_id.revision_battery_ids.type_battery_id')
    def _compute_selected_type_battery_ids(self):
        for record in self:
            record.selected_type_battery_ids = record.mapped('revision_id.revision_battery_ids.type_battery_id')

    def _domain_type_battery_id(self):
        return [('id', 'not in', self.selected_type_battery_ids.ids),
                ('behavior', '=', 'battery')
                ]

    offer_battery_model = fields.Char(
        string="Battery Model",
    )

    offer_battery_capacity = fields.Float(
        string="Battery Capacity (kWh)",
        digits=(16, 1),
    )

    offer_battery_power = fields.Float(
        string="Battery Power (kWn)",
        digits=(16, 1),
    )

    offer_battery_quantity = fields.Integer(
        string="Battery Quantity",
    )
