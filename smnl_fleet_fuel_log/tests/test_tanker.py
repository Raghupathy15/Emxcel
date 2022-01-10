# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tests import common
from odoo.exceptions import ValidationError


# from odoo.tests.common import TransactionCase


class TestTanker(common.TransactionCase):

    def setUp(self):
        super(TestTanker, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(TestTanker, cls).setUpClass()

        # Customer related data
        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Julia Agrolait',
            'email': 'julia@agrolait.example.com',
        })
        # product
        cls.product = cls.env['product.product'].create({'name': 'Office Lamp'})
        # responsible person
        cls.hr_employee = cls.env['hr.employee'].create({'name': 'Employee-1'})
        # partner
        cls.res_partner = cls.env['res.partner'].create({'name': 'vendor-partner-1',
                                                         'supplier': True})
        # tanker master
        fleet_tanker_master = cls.env['fleet.tanker'].create({'name': 'new',
                                                              'product_id': cls.product.id,
                                                              'responsible_id': cls.hr_employee.id,
                                                              'vendor_id': cls.res_partner.id,
                                                              'date_purchase': datetime.today(),
                                                              'qty': 100,
                                                              'notify_qty': 50,
                                                              'amount': 10000,
                                                              'state': 'draft', })
        fleet_tanker_master.action_confirm()

    def test_negative_qty(self):
        super(TestTanker, self).test_negative_qty()

        # Customer related data
        partner_1 = self.env['res.partner'].create({
            'name': 'Julia Agrolait',
            'email': 'julia@agrolait.example.com',
        })
        # product
        product = self.env['product.product'].create({'name': 'Office Lamp'})
        # responsible person
        hr_employee = self.env['hr.employee'].create({'name': 'Employee-1'})
        # partner
        res_partner = self.env['res.partner'].create({'name': 'vendor-partner-1',
                                                      'supplier': True})
        fleet_tanker_master1 = self.env['fleet.tanker'].sudo().create({'name': 'new',
                                                                       'product_id': product.id,
                                                                       'responsible_id': hr_employee.id,
                                                                       'vendor_id': res_partner.id,
                                                                       'date_purchase': datetime.today(),
                                                                       'qty': 100,
                                                                       'notify_qty': 50,
                                                                       'amount': 10000,
                                                                       'state': 'draft', })
        self.assertLessEqual(fleet_tanker_master1.notify_qty, 100, "Notify quantity should be greater then 100!")
        self.assertGreaterEqual(fleet_tanker_master1.notify_qty, 100, "Notify quantity should be less then 100!")
        # confirm tanker

    # test_negative_qty()
