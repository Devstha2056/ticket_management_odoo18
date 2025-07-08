from odoo import models, api, fields


class Team(models.Model):
    _name = "ticket.team"
    _description = "Ticket Team"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'department_id'

    department_id = fields.Many2one('hr.department', string='Department', required=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, tracking=True)

    user_id = fields.Many2one('res.users', string='Responsible User', default=lambda self: self.env.user, tracking=True,
                              domain="[('company_id', '=', company_id)]")

    email = fields.Char(string='Email')

    employee_ids = fields.Many2many('hr.employee', string='Member')



