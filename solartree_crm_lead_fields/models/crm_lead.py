##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    solartree_code = fields.Char(
        string="Lead Code",
        required=True,
        copy=False
    )
    solartree_lead_type_id = fields.Many2one(
        comodel_name="crm.lead.type",
        string="Lead Type",
        help="Type of the lead"
    )

    _sql_constraints = [
        ("crm_lead_unique_solartree_code", "UNIQUE (solartree_code)", _("The lead code must be unique!")),
    ]

