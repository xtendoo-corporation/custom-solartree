from odoo import models, fields, api

class ProjectTaskInherited(models.Model):
    _inherit = 'project.task'

    def _compute_director_of_operations_email(self):
        director_of_operations = self.env['res.users'].search([('groups_id', '=', 'solartree.group_director_of_operations')])
        self.director_of_operations_email = director_of_operations.email


    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'done':
            if self.milestone_id:
                self.send_notification()

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
            'subject': 'Task Completed',
            'body_html': 'Task %s has been completed' % self.name,
            'email_to': 'recipient@example.com', #usuario del grupo... Director de Operaciones
            'message_type': 'email',
        }
        self.env['mail.mail'].create(mail_values).send()

    def send_date_modified_notification(self, date_modified):
        mail_values = {
            'subject': 'Task Dates Changed',
            'body_html': date_modified,
            'email_to': 'a@a.com', #usuario del grupo... Director de Operaciones
            'message_type': 'email',
        }
        self.env['mail.mail'].create(mail_values).send()
