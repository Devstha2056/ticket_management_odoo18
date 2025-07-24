from datetime import datetime, timedelta
import pytz
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import  logging
_logger = logging.getLogger(__name__)


class TicketsManagement(models.Model):
    _name = 'ticket.management'
    _description = 'Ticket Module'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'random_ticket'
    _order='random_ticket desc'

     # Core Fields
    team_id = fields.Many2one('ticket.team', string='Team')
    employee_ids = fields.Many2many('hr.employee',related='team_id.employee_ids',string='Team Members', readonly=True)
    employee_ids_id = fields.Many2one('hr.employee',string='Assign User', domain="[('id', 'in', employee_ids)]")
    manager_ids = fields.Many2one('hr.employee',related='team_id.manager_id',string='Manager', readonly=True)
    manager_ids_id = fields.Many2one('hr.employee',string='Assign Manager', domain="[('id', 'in', manager_ids)]")
    # Employee and Department Fields
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company,tracking=True)

    user_id = fields.Many2one('res.users', string='Responsible User', default=lambda self: self.env.user, tracking=True,
                              domain="[('company_id', '=', company_id)]")
    
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True, tracking=True)   

    customer_id = fields.Many2one('res.partner', string='Customer', default=lambda self: self.env.user.partner_id,tracking=True)
    ticket_type = fields.Many2one('ticket.type', string='Ticket Type')

    priority = fields.Selection([
        ('urgent', 'P1-Urgent'),
        ('high', 'P2-High'),
        ('medium', 'P3-Medium'),
        ('low', 'P4-Low'),

    ],store=True, tracking=True)

    def action_open_priority_wizard(self):
        return {
            'name': 'Change Priority',
            'type': 'ir.actions.act_window',
            'res_model': 'priority.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
    # Menu Fields
    parent = fields.Many2one('solution.type', string='Parent Module')
    child_menu = fields.Many2one('menu.module', string='Child Module', domain="[('parent_id', '=', parent)]")
    grandchild_menu = fields.Many2one('menu.option', string='Grandchild Module',domain="[('child_id', '=', child_menu)]")
    child_menu_ids = fields.Many2many('menu.module', string='Child Menus')
    grandchild_menu_ids = fields.Many2many('menu.option', string='Grandchild Menus')

    # State Fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('acknowledgement', 'Acknowledgement'),
        ('work_in', 'Work In Progress'),
        ('work_out', 'Work Delivered'),
        ('client_feedback', 'Client Feedback'),
        ('closed', 'Closed'),
    ], default='draft', tracking=True)

    # Remark Fields
    remark = fields.Text(string='Remarks', required=True, tracking=True, store=True)
    all_remarks = fields.Text("All Remarks", compute='_compute_all_remarks', store=True)

    @api.depends('remark')
    def _compute_all_remarks(self):
        stages = self.state
        for record in self:
            if record.remark:
                remark_count = len(record.all_remarks.split("\n")) if record.all_remarks else 0
                stage_label = stages[remark_count] if remark_count < len(stages) else "Extra Remark"
                new_remark = f"{self.state}: {self.env.user.name}: {record.remark}"
                record.all_remarks = (record.all_remarks + "\n" if record.all_remarks else "") + new_remark

    # Date Fields
    create_date = fields.Datetime(string='Created Date', default=fields.Datetime.now, store=True)
    last_stage_update = fields.Datetime(string='Last Stage Update')
    assigned_date = fields.Datetime(string='Assigned Date', default=fields.Datetime.now)
    feedback_date = fields.Datetime(string='Feedback Date')
    closed_date = fields.Datetime(string='Closed Date')
    today = fields.Date(string='Today', compute='_compute_today')

    def _compute_today(self):
        for record in self:
            record.today = fields.Date.context_today(self)

    # other information
    phone = fields.Char(string='Phone Number', compute='_compute_phone', store=True)

    @api.depends('customer_id.phone')
    def _compute_phone(self):
        for rec in self:
            rec.phone = rec.customer_id.phone if rec.customer_id else ''

    email = fields.Char(string='Email', compute='_compute_email', store=True)

    @api.depends('customer_id')
    def _compute_email(self):
        for record in self:
            record.email = record.customer_id.email if record.customer_id else ''

    description = fields.Html(string='Description', store=True)
    customer_rating = fields.Selection(selection=[
        ('1', 'Very Bad'),
        ('2', 'Bad'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ],
        string="Customer Rating?",
        help="Rating given to the customer."
    )
    comment = fields.Text(string="Comment", help="Additional comments or feedback about the customer.")

    # Image Attachments Fields
    capture_images = fields.One2many('image.storage', 'image_id', string='Attached Images', store=True, tracking=True)
    capture_image = fields.Binary(string='Attached File', store=True)
    # Random Code and Sequence Fields
    random_code = fields.Char(string='Random Code', readonly=True)
    sequence_number = fields.Integer(string='Sequence Number', default=1)
    random_ticket = fields.Char(string='Random Ticket', readonly=True,index=True)

#SLA POLICY

    respond_deadline = fields.Datetime(string='Respond Deadline', compute='_compute_deadline', store=True,readonly=True)
    resolve_deadline = fields.Datetime(string='Resolve Deadline', compute='_compute_deadline', store=True,readonly=True)
    sla_response_status = fields.Char(string='SLA  Response Status', store=True, readonly=True)
    sla_resolve_status = fields.Char(string='SLA Resolve Status', store=True, readonly=True)

#sla time
    @api.depends('priority')
    def _compute_deadline(self):
        for record in self:
            if record.priority:
                now = datetime.now()
                if record.priority == 'urgent':
                    record.respond_deadline = now + timedelta(minutes=30)
                    record.resolve_deadline = now + timedelta(hours=4)
                elif record.priority == 'high':
                    record.respond_deadline = now + timedelta(hours=1)
                    record.resolve_deadline = now + timedelta(hours=24)
                elif record.priority == 'medium':
                    record.respond_deadline = now + timedelta(hours=4)
                    record.resolve_deadline = now + timedelta(hours=72)
                elif record.priority == 'low':
                    record.respond_deadline = now + timedelta(hours=8)
                    record.resolve_deadline = now + timedelta(hours=120)
            else:
                record.respond_deadline = False
                record.resolve_deadline = False

    @api.model
    def auto_change_sla_respond_status(self):
        records = self.env['ticket.management'].search([])
        for record in records:
            now = fields.Datetime.now()
            sla_pass_respond = False
            # Only check the SLA status for 'acknowledgement' state or after
            if record.state in ['acknowledgement', 'work_in', 'work_out', 'client_feedback',
                                'closed'] and record.respond_deadline:
                sla_pass_respond = now <= record.respond_deadline  # Respond deadline must be before or equal to now

            if record.state in ['acknowledgement', 'work_in', 'work_out', 'client_feedback',
                                'closed']:  # Update SLA status if the state is any after 'acknowledgement'
                if sla_pass_respond:
                    record.sla_response_status = 'SLA RESPOND DONE'
                else:
                    record.sla_response_status = 'SLA RESPOND INCOMPLETE'


    def auto_change_sla_resolve_status(self):
        records = self.env['ticket.management'].search([])
        for record in records:
            now = fields.Datetime.now()
            sla_pass_resolve = False
            # Only check the SLA status for 'closed' state
            if record.state == 'closed' and record.resolve_deadline:
                sla_pass_resolve = now <= record.resolve_deadline

            if record.state == 'closed':  # Only update SLA status if the state is 'closed'
                if sla_pass_resolve:
                    record.sla_resolve_status = 'SLA RESOLVE DONE'
                else:
                    record.sla_resolve_status = 'SLA RESOLVE INCOMPLETE'

    sla_status_done_count = fields.Integer(
        string="SLA Status Done Count",
        compute='_compute_sla_status_done_count',
        store=True
    )

    @api.depends('sla_response_status', 'sla_resolve_status')
    def _compute_sla_status_done_count(self):
        for record in self:
            # Search for records where both SLA statuses are "DONE"
            done_records = self.env['ticket.management'].search([
                ('sla_response_status', '=', 'SLA RESPOND DONE'),
                ('sla_resolve_status', '=', 'SLA RESOLVE DONE')
            ])
            # Set the count to the number of matching records
            record.sla_status_done_count = len(done_records)


    # State Management Methods
    def action_confirm(self):
        self._check_state('draft', 'open', "Only draft tickets can be confirmed.")
        admin_users = self.env['res.users'].search(
            [('groups_id', 'in', self.env.ref('tickets_management.group_admin').id)])  # Searching for admin users
        admin_partner_ids = [user.partner_id.id for user in admin_users if
                             user.partner_id]  # Get partner_ids of admin users

        if admin_partner_ids:
            self.message_post(
                partner_ids=admin_partner_ids,
                subject="Ticket Created",
                body=f"A new ticket with number {self.random_ticket} has been created.",
            )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Ticket Created',  # Notification title
                'message': 'Your Ticket was created successfully!',  # Notification message
                'type': 'success',  # Notification type (success, warning, danger, info)
                'sticky': False,  # Optional: If True, the notification stays until dismissed
                'next': {'type': 'ir.actions.act_window_close'},  # Optional: Close the wizard after notification
            }
        }

    def action_assign(self):
        self._check_state('acknowledgement', 'work_in', "Please assign the ticket first!")

        if self.employee_ids_id and self.employee_ids_id.user_id and self.employee_ids_id.user_id.partner_id:
            partner_id = self.employee_ids_id.user_id.partner_id.id

            # Send in-app notification
            self.message_post(
                partner_ids=[partner_id],  # Ensure only valid partner_id is used
                subject="Ticket Assigned",
                body=f"The ticket number {self.random_ticket} has been assigned to {self.employee_ids_id}.",
            )

            # Send email notification
            template = self.env.ref('tickets_management.ticket_mail_template_assign')
            if template:
                template.send_mail(self.id, force_send=True)
        else:
            raise UserError("The assigned employee does not have a linked user or partner.")

    def action_assign_to_manager(self):
        self._check_state('work_in', 'work_in', "Please assign the ticket first!")

        if self.team_id and self.team_id.manager_id and self.team_id.manager_id.user_id and self.team_id.manager_id.user_id.partner_id:
            partner_id = self.team_id.manager_id.user_id.partner_id.id

            # Send in-app notification
            self.message_post(
                partner_ids=[partner_id],
                subject="Ticket Assigned to Manager",
                body=f"The ticket number {self.random_ticket} has been assigned to the manager {self.team_id.manager_id.name}.",
            )

            # Send email notification
            template = self.env.ref('tickets_management.ticket_mail_template_assign')
            if template:
                template.send_mail(self.id, force_send=True)
        else:
            raise UserError("The team does not have a manager with a linked user or partner.")  
        

    def action_complete(self):
        self._check_state('work_in', 'work_out', "Please check the ticket first!")

    def action_reject(self):

        self._check_state('acknowledgement', 'closed', "Please check the ticket first!")
        if self.user_id and self.user_id.partner_id:
            self.message_post(
                partner_ids=[self.user_id.partner_id.id],
                subject="Ticket Rejected",
                body=f"The ticket number {self.random_ticket} has been Rejected due to {self.remark} .",

            )
            template = self.env.ref('tickets_management.ticket_mail_template_rejected')
            if template:
                template.send_mail(self.id, force_send=True)

                 


    def action_closed(self):
        self._check_state('client_feedback', 'closed', "Only client feedback tickets can be closed.")

        if self.user_id and self.user_id.partner_id:
            self.message_post(
                partner_ids=[self.user_id.partner_id.id],
                subject="Ticket Closed",
                body=f"The ticket number {self.random_ticket} has been Closed.",

            )

            template = self.env.ref('tickets_management.ticket_mail_template_closed')
            if template:
                template.send_mail(self.id, force_send=True)
            admin_users = self.env['res.users'].search(
                [('groups_id', 'in', self.env.ref('tickets_management.group_admin').id)])  # Searching for admin users
            admin_partner_ids = [user.partner_id.id for user in admin_users if
                                 user.partner_id]  # Get partner_ids of admin users

            if admin_partner_ids:
                self.message_post(
                    partner_ids=admin_partner_ids,
                    subject="Ticket Closed",
                    body=f"A new ticket with number {self.random_ticket} has been closed.",
                )
        return {
            'effect': {
                'message': 'Boom!!!!!! Your Ticket has Been Closed!!!.Dont forget to give us review!!!!',
                'type': 'rainbow_man',
            }
        }

    def get_signup_url(self):
        """Generate URL to open the specific ticket"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&model=ticket.management&view_type=form"

    def action_open(self):
        self._check_state('client_feedback', 'draft', "Only client feedback tickets can be closed.")


    def action_acknowledgement(self):
        self._check_state('open', 'acknowledgement', "Please confirm the ticket first.")
        if not self.env.user.email:
            raise UserError(
                "Your email is not set. Please configure your email in user settings before doing acknowledgment.")

        if self.user_id and self.user_id.partner_id:
            self.message_post(
                partner_ids=[self.user_id.partner_id.id],
                subject="Ticket Acknowledgement",
                body=f"The ticket number {self.random_ticket} has been Acknowledgement.",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
            template = self.env.ref('tickets_management.ticket_mail_template')
            if template:
                template.send_mail(self.id, force_send=True)

    def action_feedback(self):
        self._check_state('work_out', 'client_feedback', "Please Confirmed the work first.")



    def _check_state(self, required_state, new_state, error_message):
        for ticket in self:
            if ticket.state != required_state:
                raise UserError(error_message)
            ticket.state = new_state

    # for email
    def action_send_email(self):
        template = self.env.ref('tickets_management.ticket_mail_template')
        for rec in self:
            if rec.customer_id.email:
               # Corrected to use `rec` instead of `self`
                email_values = {
                    'email_cc': False,
                    'auto_delete': True,
                    'recipient_ids': [],
                    'partner_ids': [],
                    'scheduled_date': False,
                }
                template.send_mail(rec.id, force_send=True, email_values=email_values)
            else:
                raise UserError("Email not found for record: %s" % rec.random_ticket)

      #curd
    @api.model
    def create(self, vals):
        # vals['random_code'] = self.generate_random_code
        if vals.get("random_ticket", "New") == "New":
            vals["random_ticket"] = self.env["ir.sequence"].next_by_code("ticket.management") or 'New'

        return super(TicketsManagement, self).create(vals)
#self write
    def write(self, vals):
        if 'state' in vals:
            vals['last_stage_update'] = fields.Datetime.now()

            if vals['state'] == 'closed':
                vals['closed_date'] = fields.Datetime.now()

            if vals['state'] == 'client_feedback':
                vals['feedback_date'] = fields.Datetime.now()

            if vals.get('state') != self.state and vals.get('state') in ['acknowledgement', 'work_in', 'client_feedback']:
                vals['remark'] = ''

        return super().write(vals)
#deleting Function
    def unlink(self):
        for record in self:
            if record.state not in ['draft', 'open']:
                raise UserError(
                    "You can only delete tickets are in Draft and Open state!"
                )
        return super().unlink()
#auto closed ticket
    @api.model
    def auto_close_tickets(self):
        now = fields.Datetime.now()
        today_start = datetime.combine(now, datetime.min.time())
        two_days_ago = now - timedelta(days=2)

        tickets_to_close = self.search([
            ('state', '=', 'client_feedback'),

        ])
        _logger.info(f'================hii dev========={tickets_to_close}================================')

        for record in tickets_to_close:
            record.write({'state': 'closed', 'closed_date': now })

#dashboard details
    def get_details(self):
        """ Returns different counts for displaying in dashboard"""
        today = datetime.today()
        tz_name = self.env.user.tz
        today_utc = pytz.timezone('UTC').localize(today,
                                                  is_dst=False)
        context_today = today_utc.astimezone(pytz.timezone(tz_name))

        company_id=self.env.company.id

        total_tickets = self.env['ticket.management'].search_count([])

        total_open = self.env['ticket.management'].search_count(
            [('state', '=', 'open')])

        total_wip = self.env['ticket.management'].search_count(
            [('state', '=', 'work_in')])

        total_wot = self.env['ticket.management'].search_count(
            [('state', '=', 'work_out')])

        total_closed = self.env['ticket.management'].search_count(
            [('state', '=', 'closed')])

        total_urgent = self.env['ticket.management'].search_count([
            ('priority', '=', 'urgent'),
            ('state', '!=', 'closed')
        ])
        total_high = self.env['ticket.management'].search_count([
            ('priority', '=', 'high'),
            ('state', '!=', 'closed')
        ])
        total_medium = self.env['ticket.management'].search_count([
            ('priority', '=', 'medium'),
            ('state', '!=', 'closed')
        ])
        total_low = self.env['ticket.management'].search_count([
            ('priority', '=', 'low'),
            ('state', '!=', 'closed')
        ])

        staff = self.env['res.users'].search_count(
            [('groups_id', 'in',
              [self.env.ref('tickets_management.group_user').id,
               self.env.ref(
                   'tickets_management.group_employee').id,
               self.env.ref(
                   'tickets_management.group_admin').id,

               ])])

        return {
            'total_tickets': total_tickets,
            'total_open': total_open,
            'total_wip': total_wip,
            'total_wot': total_wot,
            'total_closed': total_closed,
            'total_urgent': total_urgent,
            'total_high': total_high,
            'total_medium': total_medium,
            'total_low': total_low,
            'staff': staff,
            'company_id': company_id,

        }