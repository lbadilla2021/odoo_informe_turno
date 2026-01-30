# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import ValidationError


class ITOrdenServicio(models.Model):
    _name = "it.orden.servicio"
    _description = "Orden de Servicio"
    _rec_name = "descripcion_servicio"

    name = fields.Char("ID", required=True)
    numero_pedido = fields.Char("Número de pedido", required=True)
    ito = fields.Char("ITO")
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
    fecha_adjudicacion = fields.Date("Fecha Adjudicación")
    fecha_inicio_programada = fields.Date("Fecha Inicio Programada")
    fecha_termino_programada = fields.Date("Fecha Término Programada")
    duracion_horas = fields.Float("Duración (horas)", required=True)
    cantidad_equipos = fields.Integer("Cantidad de equipos", required=True)
    valor_adjudicado = fields.Float("Valor Adjudicado")
    valor_final = fields.Float("Valor Final")
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

    def _check_required_fields(self, field_names, action_name):
        missing_fields = [
            self._fields[field].string
            for field in field_names
            if (
                self[field] is False
                or self[field] is None
                or (isinstance(self[field], str) and not self[field].strip())
            )
        ]
        if missing_fields:
            raise ValidationError(
                "Debe completar los siguientes campos para %s: %s"
                % (action_name, ", ".join(missing_fields))
            )

    def action_descartar(self):
        for record in self:
            record.estado = "perdido"

    def action_adjudicar(self):
        for record in self:
            record._check_required_fields(
                ["cliente_id", "establecimiento_id", "tipo_trabajo_id", "tipo_servicio_id"],
                "adjudicar",
            )
            if not record.fecha_adjudicacion:
                record.fecha_adjudicacion = fields.Date.context_today(record)
            record.estado = "adjudicado"

    def action_planificar(self):
        for record in self:
            record._check_required_fields(
                ["ito", "fecha_inicio_programada", "fecha_termino_programada"],
                "planificar",
            )
            record.estado = "planificado"

    def action_cobrar(self):
        for record in self:
            record._check_required_fields(
                ["valor_adjudicado", "valor_final"],
                "cobrar",
            )
            record.estado = "por_cobrar"

    def action_cerrar(self):
        for record in self:
            record.estado = "cobrado"
