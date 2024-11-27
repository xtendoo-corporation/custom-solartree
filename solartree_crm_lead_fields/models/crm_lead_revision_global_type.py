from odoo import fields, models

class CrmLeadRevisionPrices(models.Model):
    _name = "crm.lead.revision.global.type"
    _description = "Lead Revision Global Type"

    name = fields.Char(
        string="Name",
        required=True
    )

    behavior = fields.Selection(
        selection=[
            ('fee_and_margins', 'Fee and Margins'),
            ('total_price', 'Total Price'),
            ('direct_costs', 'Direct Costs'),
            ('inverter', 'Inverter'),
            ('battery', 'Battery'),
            ('energy_simulation', 'Energy Simulation'),
        ],
        string="Behavior",
        required=True
    )

    behavior_extra = fields.Selection(
        selection=[
            ('project', 'Proyecto'),
            ('solartree', 'Solartree'),
        ],
        string="Behavior Extra",
    )

    project = fields.Boolean(
        string="Project",
    )

    solartree = fields.Boolean(
        string="Solartree",
    )

