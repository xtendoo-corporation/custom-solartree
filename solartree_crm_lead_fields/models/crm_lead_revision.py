from odoo import models, fields, api


class CrmLeadRevision(models.Model):
    _name = 'crm.lead.revision'
    _description = 'Lead Revision'

    name = fields.Char(string="Revision Name", required=True)
    lead_id = fields.Many2one('crm.lead', string="Opportunity", required=True, ondelete='cascade')
    offer_kwp = fields.Float(
        'Offer kWp'
    )
    offer_kwn = fields.Float(
        'Offer kWn'
    )
    offer_storage_kwh = fields.Float(
        'Offer storage kWh'
    )
    offer_storage_kwn = fields.Float(
        'Offer storage kWn'
    )
    offer_ve_kwn = fields.Float(
        'Offer VE kWh'
    )
    offer_tot = fields.Many2one(
        comodel_name="crm.tot",
        string="TOT revisions field",
    )
    offer_HT = fields.Float(
        'Offer HT'
    )
    offer_date_deliver = fields.Date(
        'Offer deliver date'
    )
    offer_HT = fields.Float(
        'Offer HT'
    )
    offer_fee_external = fields.Float(
        'Offer fee external'
    )
    offer_fee_internal = fields.Float(
        'Offer fee internal'
    )
    offer_gg = fields.Float(
        'Offer GG'
    )
    offer_bi = fields.Float(
        'Offer BI'
    )
    offer_mbsv = fields.Float(
        'Offer MBSV',
        readonly=True,
    )
    offer_fv_price = fields.Monetary(
        'Offer FV price',
        currency_field='company_currency',
    )
    offer_wp = fields.Float(
        'Offer €/Wp',
        readonly=True,
    )
    offer_pb_actual = fields.Float(
        'PB actuals'
    )
    offer_tir_actual = fields.Float(
        'TIR actuals'
    )
    offer_pb_omip = fields.Float(
        'PB OMIP'
    )
    offer_tir_omip = fields.Float(
        'TIR OMIP'
    )
    offer_pb_proyection = fields.Float(
        'PB proyection'
    )
    offer_tir_proyection = fields.Float(
        'TIR proyection'
    )
    offer_storage_price = fields.Monetary(
        'Offer storage price',
        currency_field='company_currency',
    )
    offer_ve_price = fields.Monetary(
        'Offer VE Price',
        currency_field='company_currency',
    )
    company_currency = fields.Many2one("res.currency", string='Currency', compute="_compute_company_currency",
                                       compute_sudo=True)

    @api.depends('lead_id.company_id')
    def _compute_company_currency(self):
        for record in self:
            if record.lead_id and record.lead_id.company_id:
                record.company_currency = record.lead_id.company_id.currency_id
            else:
                record.company_currency = False
                print("Lead ID or Company ID is not set for record %s", record.id)
