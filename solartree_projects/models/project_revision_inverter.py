from odoo import fields, models, api


class ProjectRevisionInverter(models.Model):
    _name = "project.revision.inverter"
    _description = "Project Revision Inverter"

    revision_id = fields.Many2one(
        "project.revision",
        required=True,
    )

    type_inverter_id = fields.Many2one(
        "crm.lead.revision.global.type",
        string="Type",
        domain=lambda self: self._domain_type_inverter_id(),
    )

    selected_type_inverter_ids = fields.Many2many(
        'crm.lead.revision.global.type',
        compute='_compute_selected_type_inverter_ids',
        store=False
    )

    @api.depends('revision_id.revision_inverter_ids.type_inverter_id')
    def _compute_selected_type_inverter_ids(self):
        for record in self:
            record.selected_type_inverter_ids = record.mapped('revision_id.revision_inverter_ids.type_inverter_id')

    def _domain_type_inverter_id(self):
        return [('id', 'not in', self.selected_type_inverter_ids.ids),
                ('behavior', '=', 'inverter')
                ]

    offer_inverter_model = fields.Char(
        string="Inverter Model",
    )

    offer_inverter_unit_power = fields.Float(
        string="Inverter Unit Power",
        digits=(16, 1),
    )

    offer_inverter_quantity = fields.Integer(
        string="Inverter Quantity",
    )
