# -*- coding: utf-8 -*-
{
    "name": "Barca Informe Turno",
    "summary": "Registro móvil de informes de turno con fotos antes/después",
    "version": '18.0.1.0.0',
    "category": "Operations",
    "author": "Apex / Barca",
    "license": "LGPL-3",
    "website": "",
    "depends": [
        "base",
        "mail",
        "hr",
        "hr_skills",   # ✅ agregado: asegura que el modelo hr.employee.tag esté disponible
        "fleet",
        "contacts",
    ],
    "assets": {
        "web.assets_backend": [
            "informe_turno/static/src/scss/informe_turno.scss",
        ],
    },
    "data": [
        "data/sequence.xml",
        "data/hr_tags.xml",
        "data/tablas_iniciales.xml",
        "data/tipo_vehiculo.xml",
        "data/clientes_establecimientos.xml",

        "security/informe_turno_groups.xml", 
        "security/informe_turno_security.xml",
        "security/ir.model.access.csv",

        "views/it_orden_servicio_views.xml",
        "views/informe_turno_views.xml",

        "menu/menu_comercial.xml",
    ],
    "application": True,
}
