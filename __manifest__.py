# -*- coding: utf-8 -*-
{
    "name": "Informe Turno",
    "summary": "Registro móvil de informes de turno con fotos antes/después",
    "version": "17.0.1.0.0",
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
            "odoo_informe_turno/static/src/css/informe_turno.css",
        ],
    },
    "data": [
        "data/sequence.xml",
        "data/hr_tags.xml",
        "data/tipo_vehiculo.xml",
        "security/informe_turno_security.xml",
        "security/ir.model.access.csv",
        "views/informe_turno_views.xml",
    ],
    "application": True,
}
