# -*- coding: utf-8 -*-
from odoo import fields, models


class ITOrdenServicio(models.Model):
    _name = "it.orden.servicio"
    _description = "Orden de Servicio"
    _rec_name = "descripcion_servicio"

    name = fields.Char("ID OS", required=True)
    numero_pedido = fields.Char("Número de pedido", required=True)
    ito = fields.Char("ITO", required=True)
    establecimiento_id = fields.Many2one(
        "res.partner",
        string="Establecimiento",
        domain="[('parent_id', '!=', False)]",
        required=True,
    )
    cliente_id = fields.Many2one(
        "res.partner",
        string="Cliente",
        domain="[('parent_id', '=', False)]",
        required=True,
    )
    descripcion_servicio = fields.Text("Descripción del servicio", required=True)
    tipo_trabajo_id = fields.Many2one(
        "it.tipo.trabajo", string="Tipo de trabajo", required=True
    )
    tipo_servicio_id = fields.Many2one(
        "it.tipo.servicio", string="Tipo de servicio", required=True
    )
    duracion_horas = fields.Float("Duración (horas)", required=True)
    cantidad_equipos = fields.Integer("Cantidad de equipos", required=True)
    estado = fields.Selection(
        selection=[
            ("licitacion", "Licitación"),
            ("perdido", "Perdido"),
            ("adjudicado", "Adjudicado"),
            ("planificado", "Planificado"),
            ("por_cobrar", "Por Cobrar"),
            ("cobrado", "Cobrado"),
        ],
        string="Estado",
        required=True,
        default="licitacion",
    )
