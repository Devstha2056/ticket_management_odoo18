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

    employee_ids = fields.Many2many('hr.employee', string='Member', domain="[('department_id', '=', department_id)]")

    manager_id = fields.Many2one('hr.employee', string='Manager')

    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id:
            self.manager_id = self.department_id.manager_id
        else:
            self.manager_id = False





