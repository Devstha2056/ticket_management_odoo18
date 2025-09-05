import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape
import requests
from odoo.exceptions import UserError

class XLSXReportController(http.Controller):
    """Controller for XlsX report"""

    @http.route('/xlsx_reports', type='http', auth='user',
                methods=['POST'], csrf=False)
    def get_room_booking_report_xlsx(self, model, options, output_format,
                                     report_name):
        """Function for generating xlsx report"""
        report_obj = request.env[model].sudo()
        options = json.loads(options)
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[('Content-Type', 'application/vnd.ms-excel'),
                             ('Content-Disposition',
                              content_disposition(report_name + '.xlsx'))]
                )
                report_obj.get_xlsx_report(options, response)
                response.set_cookie('fileToken', 'dummy token')
                return response
        except Exception as e:
            s_error = http.serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': s_error
            }
            return request.make_response(html_escape(json.dumps(error)))


class PortalTickets(http.Controller):

    @http.route(['/my/tickets'], type='http', auth='user', website=True)
    def portal_tickets(self, **kwargs):
        tickets = request.env['ticket.management'].sudo().search([
            ('customer_id', '=', request.env.user.partner_id.id)
        ])
        ticket_types = request.env['ticket.type'].sudo().search([])
        issue_types = request.env['solution.type'].sudo().search([])
        user_ids = request.env['res.users'].sudo().search([])
        banks = request.env['res.bank'].sudo().search([])
        return request.render(
            "tickets_management.portal_my_tickets",
            {
                'tickets': tickets,
                'ticket_types': ticket_types,
                'issue_types': issue_types,
                'user_ids': user_ids,
                'banks': banks,
            }
        )

    @http.route(['/my/tickets/create'], type='http', auth='user', website=True, methods=['POST'])
    def create_ticket(self, **kwargs):
        recaptcha_response = kwargs.get('g-recaptcha-response')
        recaptcha_response = kwargs.get('g-recaptcha-response')
        if not recaptcha_response:
            raise UserError("❌ Please verify that you are human by ticking the reCAPTCHA box.")

        # Verify token with Google
        secret_key = request.env['ir.config_parameter'].sudo().get_param('recaptcha_private_key')
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {'secret': secret_key, 'response': recaptcha_response}
        result = requests.post(verify_url, data=payload).json()

        if not result.get('success'):
            raise UserError("❌ reCAPTCHA verification failed. Please try again.")

        vals = {
            'sequence_number': kwargs.get('sequence_number'),
            'ticket_type': int(kwargs.get('ticket_type')) if kwargs.get('ticket_type') else False,
            'user_id': request.env.user.id,
            'parent': int(kwargs.get('parent')) if kwargs.get('parent') else False,
            'device_number': kwargs.get('device_number'),
            'bank': int(kwargs.get('bank')) if kwargs.get('bank') else False,
            'priority': kwargs.get('priority'),
            'description': kwargs.get('description'),
            'email': kwargs.get('email'),
            'phone': kwargs.get('email'),
            'company_id': request.env.company.id,
            'state': 'draft',
            'remark': kwargs.get('remark'),
        }

        ticket=request.env['ticket.management'].sudo().create(vals)
        # return request.redirect('/my/tickets')
        return request.redirect('/my/tickets/success/%s' % ticket.id)

    @http.route(['/my/tickets/success/<int:ticket_id>'], type='http', auth='user', website=True)
    def ticket_success(self, ticket_id):
        ticket = request.env['ticket.management'].sudo().browse(ticket_id)
        if not ticket.exists():
            return request.redirect('/my/tickets')

        return request.render('tickets_management.portal_ticket_success', {
            'ticket': ticket,
        })




