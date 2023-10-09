# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class producttemplate(models.Model):
    
    _inherit = 'product.template'
    course_id = fields.Many2one(
        string="Course",
        comodel_name="courses"
    )


class courses(models.Model):
    _name = 'courses'
    _description = 'Courses'

    name = fields.Char()
    attendance_ids = fields.One2many(
        string="attendance",
        comodel_name="attendance",
        inverse_name="course_id",
    )
    product_id = fields.Many2one(
        string="product_id",
        comodel_name="product.template",
    )
    state = fields.Selection(
        string="state",
        selection=[
                ('draft', 'Draft'),
                ('confirm', 'Confirm'),
                ('invoiced', 'Invoiced'),
        ],
        default='draft'
    )
    lesson_ids2 = fields.Many2many(
        string=" lesson",
        comodel_name="lesson",
    )
    room_ids = fields.Many2one(
        string="Room",
        comodel_name="room"
    )
    instructor_id = fields.Many2one(
        string="instructor",
        comodel_name="hr.employee"
    )
    attendance_counter = fields.Integer(
        string='Counter',
        )
    capcity = fields.Integer(
        string='Capcity',
    )
    max_cap = fields.Boolean(string="max", )
    

    @api.model
    def create(self,vals) :
        if vals['name']:
            products = self.env['product.template']
            product_id = products.create({'name' :   vals['name']})
            vals['product_id'] = product_id.id
        
        res =  super(courses,self).create(vals)
        _logger.exception("======================== self.res %s",res.id)
        product_id.write({'course_id' :   res.id})

        return res

    # def write(self,vals) :
    #     if self.product_id:
    #         if vals['name']:
    #             products = self.env['product.template']
    #             find_product = products.search([('id' , '=',self.product_id.id)])
    #             find_product.write({'name' :   vals['name']})

    #     return super(courses,self).write(vals)
    
   
    @api.onchange("attendance_ids")
    def _onchange_attendance_ids(self):
        attendance_len = len(self.attendance_ids)
        self.attendance_counter = attendance_len
        if attendance_len >self.capcity:
            self.max_cap = True
        else:
            self.max_cap = False
    
    def action_confirm(self):
        self.state = 'confirm'
        pass
    
    def action_create_invoice(self):
        self.state = 'invoiced'
        for student in self.attendance_ids:
            student_id = student.student_id.id
            course_id  = self.id 
            price = self.env['cource.price.list'] 
            find_course = price.search([('course_id','=',course_id),('count_from', '<=',self.capcity),('count_to', '>=',self.capcity)],limit=1)
            _logger.exception("=================price : %s ",find_course.price)
            invoice_line = [(0,0,{
                'product_id' : self.product_id.id,
                'quantity' : 1,
                'price_unit' : find_course.price,
                'account_id' :self.product_id.categ_id.property_account_income_categ_id.id
                
            })]
            move = self.env['account.move']
            crearte_move = move.create({
                'partner_id' : student_id,
                'move_type' : 'out_invoice',
                'invoice_line_ids' : invoice_line
            })
            
       
    

class room(models.Model):
    _name = 'room'
    _description = 'room'

    name = fields.Char()
    course_ids = fields.One2many(
        string="courses",
        comodel_name="courses",
        inverse_name="room_ids",
    )
    
    
class resPartner(models.Model):
    
    _inherit = 'res.partner'
    is_student = fields.Boolean(string="Is Student", )
    card_id = fields.Char()
    
    

    

class Instructor(models.Model):
    _inherit = 'hr.employee'

    course_ids = fields.One2many(
        string="courses",
        comodel_name="courses",
        inverse_name="instructor_id",
    )
    
class CoursePriceList(models.Model):
    _name = 'cource.price.list'
    _description = 'Course Price List'

    name = fields.Char()
    course_id = fields.Many2one(
        string="Course",
        comodel_name="courses"
    )
    count_from = fields.Integer(
        string='Count From',
    )
    count_to = fields.Integer(
        string='Count To',
    )
    price = fields.Float(string="Price", )
    

    
class lesson(models.Model):
    _name = 'lesson'
    _description = 'lesson'

    name = fields.Char()
    duration = fields.Float(string="Duration", )
    course_id = fields.Many2one(
        string="Course",
        comodel_name="courses"
    )
class attendance(models.Model):
    _name = 'attendance'
    _description = 'attendance'

    student_id = fields.Many2one(
        string="Student ID",
        comodel_name="res.partner"
        ,domain=[('is_student', '=', True)]
        
    )
    student_card_id = fields.Char(related="student_id.card_id")
    
    course_id = fields.Many2one(
        string="Course",
        comodel_name="courses"
    )
   
    