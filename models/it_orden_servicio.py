# -*- coding: utf-8 -*-

from odoo import fields, models


class ITOrdenServicio(models.Model):
    _inherit = "it.orden.servicio"

    informe_ids = fields.One2many(
        "it.informe",
        "orden_servicio_id",
        string="Informes de Turno",
    )
