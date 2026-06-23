# -*- coding: utf-8 -*-
{
    "name": "Barca Operaciones",
    "summary": "Registro móvil de informes de turno con fotos antes/después",
    "version": '18.0.2.1.0',
    "category": "Operations",
    "author": "Apex / Barca",
    "license": "LGPL-3",
    "website": "",
    "depends": [
        "base",
        "mail",
        "hr",
        "hr_skills",   # ✅ agregado: asegura que el modelo hr.employee.tag esté disponible
        "zhr_ajustes",
        "fleet",
        "contacts",
        "zoc_ajustes",
        "zmm_ajustes",
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
        "data/clientes_establecimientos.xml",

        "security/informe_turno_groups.xml", 
        #"security/informe_turno_security.xml",
        "security/ir.model.access.csv",

        "views/informe_turno_views.xml",
        "views/maintenance_origin_views.xml",
    ],
    "application": True,
}
