from odoo import models, fields, api

class ProjectTaskInherited(models.Model):
    _inherit = 'project.task'

    director_of_operations = fields.Char(string='Director of Operations', compute='_compute_director_of_operations_email')

    def _compute_director_of_operations_email(self):
        res = self.env['res.users'].search_read([('groups_id', 'in', self.env.ref('solartree_crm_lead_automatization.group_crm_operations_director').id)], ['email'])
        emails = set(r['email'] for r in res if r.get('email'))
        for record in self:
            record.director_of_operations = ','.join(emails)

    def write(self, vals):
        res = super(ProjectTaskInherited, self).write(vals)
        if 'state' in vals:
            if self.state == '1_done':
                if self.milestone_id:
                    self.send_notification()
        return res

    @api.onchange('start_date_planned')
    def _onchange_start_date_planned(self):
        if self.start_date_planned != "":
            date_modified = f'El usuario {self.env.user.name} ha modificado el "Inicio de la fecha planificada" a {self.start_date_planned} de la tarea {self.name}'
            self.send_date_modified_notification(date_modified)

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_end != "":
            date_modified = f'El usuario {self.env.user.name} ha modificado la "Fecha de fin" a {self.date_end} de la tarea {self.name}'
            self.send_date_modified_notification(date_modified)

    @api.onchange('date_deadline')
    def _onchange_date_deadline(self):
        if self.date_deadline != "":
            date_modified = f'El usuario {self.env.user.name} ha modificado la "Fecha planificada" a {self.date_deadline} de la tarea {self.name}'
            self.send_date_modified_notification(date_modified)

    def send_notification(self):
        mail_values = {
            'subject': 'La tarea %s ha sido completada' % self.name,
            'body_html': 'La tarea %s ha sido completada' % self.name,
            'email_to': self.director_of_operations,
            'message_type': 'email',
        }
        self.env['mail.mail'].create(mail_values).send()

    def send_date_modified_notification(self, date_modified):
        mail_values = {
            'subject': 'Fecha modificada en la tarea %s' % self.name,
            'body_html': date_modified,
            'email_to': self.director_of_operations,
            'message_type': 'email',
        }
        self.env['mail.mail'].create(mail_values).send()
