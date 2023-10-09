from odoo import models, fields, api,_
from datetime import datetime, timedelta


import logging
_logger = logging.getLogger(__name__)



class reminders(models.Model):
    _name = 'reminders'
    _inherit =  ['mail.thread', 'mail.activity.mixin']
    _description = 'reminders'
        
    
    
    
    name = fields.Char(string="Name", )
    decription = fields.Text(string="Description", )
    recipient_id = fields.Many2one(
        string="Recipient",
        comodel_name="res.users",
    )
    sender_id = fields.Many2one(
        string="Sender",
        comodel_name="res.users",
    )
    
    list_reminders_ids = fields.One2many(
        string="List Reminders",
        comodel_name="list.reminders",
        inverse_name="reminders_id",
    )

    def action_send_reminders(self):
        reminder = self.env['reminders'].search([])
        _logger.exception("========================action_send_reminders executed")
        
        for rec in reminder:
            for list_rem in rec.list_reminders_ids:
                create_date = list_rem.create_date
                last_time = list_rem.last_time
                period = list_rem.period
                period_time = list_rem.period_time
                
                dt_now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

                if last_time :
                        dt = last_time
                else :
                        dt = create_date

                        
                if period =='minute':
                        result = dt + timedelta(minutes= period_time)
                        
                if period =='day':
                        result = dt + timedelta(day= period_time)

                    
                if create_date and not last_time:
                    if result <= datetime.now() :
                        message_body = "please confirm create_date"+dt_now
                        odoobot_id = rec.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
                        send = rec.message_post(body=message_body,
                                                message_type='notification',
                                                partner_ids = [rec.recipient_id.id])
                        list_rem.last_time = datetime.now()
                elif last_time :
                    _logger.exception("========================last_time")
                    if result <= datetime.now() :
                        _logger.exception("========================result last_time")
                        
                        message_body = "please confirm last_time"+dt_now
                        odoobot_id = rec.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
                        send = rec.message_post(body=message_body,
                                                    message_type='notification',
                                                    partner_ids = [rec.recipient_id.id])
                        list_rem.last_time = datetime.now()
                    

class ListReminders(models.Model):
    _name = 'list.reminders'
    _description = 'List Reminders'
    
    period = fields.Selection(
        string="Period Time",
        selection=[
                ('minute', 'Minute'),
                ('hour', 'Hour'),
                ('day', 'Day'),
                ('month', 'Month'),
                ('year', 'Year'),
        ],
    )
    period_time = fields.Float(string="Period Time", )
    reminders_id = fields.Many2one(
        string="reminders",
        comodel_name="reminders",
    )
    last_time = fields.Datetime(string="last_time", )

