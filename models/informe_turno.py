# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo import models, fields

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    job_family_id = fields.Many2one(
        'hr.job.family',
        string='Familia de Cargo',
        related='job_id.job_family_id',
        readonly=True,
    )

def _quarter_hour_selection(self):
    sels = []
    for h in range(0, 24):
        for m in (0, 15, 30, 45):
            # ⚠️ Guardar valores como *string*, no float
            val = f"{h:02d}:{m:02d}"
            label = val
            sels.append((val, label))
    return sels

class ITArea(models.Model):
    _name = "it.area"
    _description = "Área"

    name = fields.Char("Nombre", required=True)
    active = fields.Boolean(default=True)


class ITEspecialidad(models.Model):
    _name = "it.especialidad"
    _description = "Especialidad"

    name = fields.Char("Nombre", required=True)
    active = fields.Boolean(default=True)


class ITTipoVehiculo(models.Model):
    _name = "it.tipo.vehiculo"
    _description = "Tipo de vehículo legado"

    name = fields.Char("Nombre", required=True)
    active = fields.Boolean(default=True)




class ITInformeFotoPair(models.Model):
    _name = "it.informe.foto.pair"
    _description = "Par de fotos Antes/Después"
    _order = "sequence, id"

    informe_id = fields.Many2one("it.informe", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    etiqueta = fields.Char("Etiqueta")
    foto_antes = fields.Image("Foto Antes", required=True, max_width=1920, max_height=1920)
    foto_despues = fields.Image("Foto Después", required=True, max_width=1920, max_height=1920)


class ITInformeVehiculo(models.Model):
    _name = "it.informe.vehiculo"
    _description = "Vehículo asociado al informe"

    informe_id = fields.Many2one("it.informe", required=True, ondelete="cascade")
    tipo_vehiculo_id = fields.Many2one(
        "fleet.vehicle.model.category", string="Tipo de vehículo", required=True
    )
    vehiculo_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehículo",
        required=True,
        domain="[('category_id', '=', tipo_vehiculo_id)]",
    )
    medida = fields.Integer("Kms/Horas", required=True)
    lts_petroline = fields.Float("Lts Petroline", digits=(16, 2))

    @api.onchange("tipo_vehiculo_id")
    def _onchange_tipo_vehiculo_id(self):
        for record in self:
            if (
                record.vehiculo_id
                and record.vehiculo_id.category_id != record.tipo_vehiculo_id
            ):
                record.vehiculo_id = False

    @api.onchange("vehiculo_id")
    def _onchange_vehiculo_id(self):
        for record in self:
            if record.vehiculo_id and not record.tipo_vehiculo_id:
                record.tipo_vehiculo_id = record.vehiculo_id.category_id

    @api.constrains("tipo_vehiculo_id", "vehiculo_id")
    def _check_vehiculo_categoria(self):
        for record in self.filtered(lambda line: line.tipo_vehiculo_id and line.vehiculo_id):
            if record.vehiculo_id.category_id != record.tipo_vehiculo_id:
                raise ValidationError(
                    _("El vehículo seleccionado debe pertenecer al tipo de vehículo indicado.")
                )

    def init(self):
        self.env.cr.execute(
            """
            UPDATE it_informe_vehiculo AS line
               SET tipo_vehiculo_id = category.id
              FROM it_tipo_vehiculo AS old_type,
                   fleet_vehicle_model_category AS category
             WHERE line.tipo_vehiculo_id = old_type.id
               AND lower(category.name) = lower(old_type.name)
            """
        )


class ITInforme(models.Model):
    _name = "it.informe"
    _description = "Informe de Turno"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El Código debe ser único.'),
    ]

    @api.constrains("doc_informe_turno", "doc_informe_capacitacion")
    def _check_required_documents(self):
        for rec in self:
            if not rec.doc_informe_turno:
                raise ValidationError(_("Debe adjuntar el archivo de Informe de Turno."))
            if not rec.doc_informe_capacitacion:
                raise ValidationError(_("Debe adjuntar el archivo de Informe de Capacitación."))
    
    def action_download_turno(self):
        self.ensure_one()
        if not self.doc_informe_turno:
            raise ValidationError(_("No hay archivo para descargar."))
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/doc_informe_turno/{self.doc_informe_turno_name}?download=true',
            'target': 'new',
        }

    def action_download_capacitacion(self):
        self.ensure_one()
        if not self.doc_informe_capacitacion:
            raise ValidationError(_("No hay archivo para descargar."))
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/doc_informe_capacitacion/{self.doc_informe_capacitacion_name}?download=true',
            'target': 'new',
        }

    
    name = fields.Char("Nombre", compute="_compute_name", store=True)
    code = fields.Char("Código", copy=False, index=True, required=True)

    supervisor_id = fields.Many2one("res.users", string="Supervisor", default=lambda self: self.env.user, required=True, tracking=True)
    fecha_ejecucion = fields.Date("Fecha de ejecución", default=fields.Date.context_today, required=True, tracking=True)
    establecimiento_id = fields.Many2one("res.partner", string="Establecimiento", domain="[('parent_id','!=',False)]", required=True, tracking=True)
    orden_servicio_id = fields.Many2one(
        "it.orden.servicio",
        string="Proyecto",
        domain="[('estado', '=', 'adjudicado')]",
        required=False,
    )
    proyecto_codigo = fields.Char(
        string="Código de Proyecto",
        related="orden_servicio_id.name",
        readonly=True,
    )
    proyecto_nombre = fields.Text(
        string="Nombre de Servicio",
        related="orden_servicio_id.descripcion_servicio",
        readonly=True,
    )

    hora_entrada_real = fields.Selection(selection=_quarter_hour_selection,string="Hora entrada real",required=True)
    hora_entrada_real_fecha = fields.Date(
        string="Fecha hora entrada real",
        compute="_compute_time_dates",
        store=True,
        readonly=True,
    )
    hora_inicio_faena = fields.Selection(selection=_quarter_hour_selection,string="Hora inicio faenal",required=True)
    hora_inicio_faena_fecha = fields.Date(
        string="Fecha hora inicio faena",
        compute="_compute_time_dates",
        store=True,
        readonly=True,
    )
    hora_fin_faena = fields.Selection(selection=_quarter_hour_selection,string="Hora fin faena", required=True)
    hora_fin_faena_fecha = fields.Date(
        string="Fecha hora fin faena",
        compute="_compute_time_dates",
        store=True,
        readonly=True,
    )
    hora_salida_real = fields.Selection(selection=_quarter_hour_selection,string="Hora salida real",required=True)
    hora_salida_real_fecha = fields.Date(
        string="Fecha hora salida real",
        compute="_compute_time_dates",
        store=True,
        readonly=True,
    )

    descripcion = fields.Text("Descripción", required=True)
    area_id = fields.Many2one("it.area", string="Área", required=True)
    nombre_equipo = fields.Char("Nombre Equipo", required=True)
    tag = fields.Char("TAG", required=True)
    tipo_trabajo_id = fields.Many2one("it.tipo.trabajo", string="Tipo de trabajo", required=True)
    tipo_servicio_id = fields.Many2one("it.tipo.servicio", string="Tipo de servicio")
    especialidad_id = fields.Many2one("it.especialidad", string="Especialidad", required=True)
    observaciones_servicio = fields.Text("Observaciones del servicio")

    ito_planta = fields.Char("ITO planta", required=True)
    prevencionista_id = fields.Many2one("hr.employee", string="Prevencionista", domain="[('job_family_id.name', '=', 'Prevencionistas')]")
    
    
    #operador_id = fields.Many2one("hr.employee", string="Operador", required=True)
    #operador_servicio_id = fields.Many2one("hr.employee", string="Operador Servicio", required=True)


    # Operadores de servicio
    # Operadores
    operador_ids = fields.Many2many(
    'hr.employee',
    'it_informe_operadores_rel',
    'informe_id',
    'employee_id',
    string='Operadores',
    domain="[('job_family_id.name', 'in', ['Operativos Mantención', 'Operativos Operación'])]"
)

        # Operadores de Servicio
    operador_servicio_ids = fields.Many2many(
        'hr.employee',
        'it_informe_operadores_servicio_rel',
        'informe_id',
        'employee_id',
        string='Operadores de Servicio',
        domain="[('job_family_id.name', 'in', ['Operativos Mantención', 'Operativos Operación'])]"
    )

    vehiculo_line_ids = fields.One2many(
        "it.informe.vehiculo", "informe_id", string="Vehículos", required=True
    )

    vehiculo_count = fields.Integer("Vehículos", compute="_compute_resource_counts")

    alojamiento = fields.Boolean("Alojamiento", default=False)
    cant_personas = fields.Integer("Cantidad de personas", required=True)
    barreras_quimica = fields.Boolean("Barreras química", default=False)
    cant_barreras_quimicas = fields.Integer("Cantidad barreras químicas", required=True)
    aspirado_alta_temperatura = fields.Boolean("Aspirado alta temperatura", default=False)

    #doc_informe_turno = fields.Binary("Informe Turno (PDF)", attachment=True)
    #doc_informe_capacitacion = fields.Binary("Informe Capacitación (PDF)", attachment=True)

    doc_informe_turno = fields.Binary(string="Informe de Turno")
    doc_informe_turno_name = fields.Char(string="Nombre Archivo Turno")

    doc_informe_capacitacion = fields.Binary(string="Informe de Capacitación")
    doc_informe_capacitacion_name = fields.Char(string="Nombre Archivo Capacitación")

    foto_pair_ids = fields.One2many("it.informe.foto.pair", "informe_id", string="Fotos antes/después")

    @api.depends("code")
    def _compute_name(self):
        for rec in self:
            rec.name = rec.code or _("Informe")

    @api.model_create_multi
    def create(self, vals_list):
        self._prepare_proyecto_values(vals_list)
        for vals in vals_list:
            code = (vals.get("code") or "").strip()
            if not code:
                raise ValidationError(_("Debe ingresar el Código (folio en papel)."))
            vals["code"] = code
            if not vals.get("supervisor_id"):
                vals["supervisor_id"] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        values = dict(vals)
        if "supervisor_id" in values:
            values.pop("supervisor_id", None)
        self._prepare_proyecto_values([values])
        return super().write(values)

    @api.onchange("orden_servicio_id")
    def _onchange_orden_servicio_id(self):
        for record in self:
            if record.orden_servicio_id:
                record.update(record._get_proyecto_values(record.orden_servicio_id))

    def _prepare_proyecto_values(self, vals_list):
        proyectos = self.env["it.orden.servicio"].browse(
            [
                vals["orden_servicio_id"]
                for vals in vals_list
                if vals.get("orden_servicio_id")
            ]
        ).exists()
        proyectos_by_id = {proyecto.id: proyecto for proyecto in proyectos}
        for vals in vals_list:
            proyecto = proyectos_by_id.get(vals.get("orden_servicio_id"))
            if proyecto:
                vals.update(self._get_proyecto_values(proyecto))

    @api.model
    def _get_proyecto_values(self, proyecto):
        return {
            "establecimiento_id": proyecto.establecimiento_id.id,
            "descripcion": proyecto.descripcion_servicio,
            "tipo_trabajo_id": proyecto.tipo_trabajo_id.id,
            "tipo_servicio_id": proyecto.tipo_servicio_id.id,
        }

    @api.depends("vehiculo_line_ids")
    def _compute_resource_counts(self):
        for rec in self:
            rec.vehiculo_count = len(rec.vehiculo_line_ids)


    @api.depends(
        "fecha_ejecucion",
        "hora_entrada_real",
        "hora_inicio_faena",
        "hora_fin_faena",
        "hora_salida_real",
    )
    def _compute_time_dates(self):
        def _to_minutes(val):
            if not val:
                return None
            h, m = map(int, val.split(":"))
            return h * 60 + m

        for rec in self:
            base_date = rec.fecha_ejecucion or fields.Date.context_today(rec)
            prev_date = base_date
            prev_time = _to_minutes(rec.hora_entrada_real)
            rec.hora_entrada_real_fecha = prev_date

            for field_name, time_value in [
                ("hora_inicio_faena_fecha", rec.hora_inicio_faena),
                ("hora_fin_faena_fecha", rec.hora_fin_faena),
                ("hora_salida_real_fecha", rec.hora_salida_real),
            ]:
                current_time = _to_minutes(time_value)
                if None not in (prev_time, current_time) and current_time < prev_time:
                    prev_date = prev_date + timedelta(days=1)
                setattr(rec, field_name, prev_date)
                prev_time = current_time if current_time is not None else prev_time


    @api.constrains("hora_entrada_real", "hora_salida_real", "hora_inicio_faena", "hora_fin_faena")
    def _check_time_order(self):
        def _to_minutes(val):
            if not val:
                return None
            h, m = map(int, val.split(':'))
            return h * 60 + m

        for rec in self:
            he = _to_minutes(rec.hora_entrada_real)
            hs = _to_minutes(rec.hora_salida_real)
            hi = _to_minutes(rec.hora_inicio_faena)
            hf = _to_minutes(rec.hora_fin_faena)

            # Si falta alguno, no validar
            if None in (he, hs, hi, hf):
                continue
            #if hs <= he:
            #    raise ValidationError(_("La hora de salida debe ser posterior a la de entrada."))
            #if hf <= hi:
            #    raise ValidationError(_("La hora fin de faena debe ser posterior al inicio de faena."))
