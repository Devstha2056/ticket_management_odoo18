from odoo import fields,api,models


class KoiliDevice(models.Model):

     _name = 'koili.device'
     _description = 'Koili Device Imformation'
     _inherit = ['mail.thread', 'mail.activity.mixin']




