# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Partner(models.Model):
    _inherit = "res.partner"


    registration_date = fields.Date(
        string="Registration Date"
    )

    geographical_scope = fields.Many2one(
        comodel_name='geographical.scope',
        string="Geographical Scope"
    )

    contact_profile = fields.Many2one(
        comodel_name='contact.profile',
        string="Contact Profile"
    )

    industrial_contact = fields.Many2one(
        comodel_name='industrial.contact',
        string="Industrial Contact",
    )

    show_industrial_contact = fields.Boolean(
        compute='_compute_show_industrial_contact',
        store=False
    )

    @api.depends('contact_profile')
    def _compute_show_industrial_contact(self):
        for record in self:
            record.show_industrial_contact = (
                record.contact_profile.name == 'Industrial' if record.contact_profile else False
            )

    associated_commercial_channel = fields.Many2one(
        comodel_name='crm.lead.channel',
        string="Associated Commercial Channel"
    )

    hr_employee_ids = fields.Many2one(
        comodel_name='hr.employee',
        string="Commercial Team",
    )

    colaborator = fields.Boolean(
        string="Colaborator",
        default=False
    )

    colaborator_type = fields.Many2one(
        comodel_name='colaborator.type',
        string="Colaborator Type"
    )
