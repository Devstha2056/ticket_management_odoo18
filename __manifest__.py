{
    'name': 'tickets_management',
    'version': '1.0.0',
    'category': 'ticketing module',
    'sequence': -100,
    'author': 'Devendra Stha',
    'summary': 'Generating tickets for support',
    'description': """
        This module provides support for clients to solve their problems.
    """,
    'depends': ['web', 'hr', 'mail', 'contacts'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data_view.xml',
        'views/view_ticket_management.xml',
        'views/configuration_view.xml',
        'views/reporting_view.xml',
        'views/closed_view.xml',
        'views/myticket_view.xml',
        'views/mail_templete_data.xml',
        'views/team_view.xml',

        'views/menu.xml',
        'views/dashboard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tickets_management/static/src/js/action_manager.js',
            'tickets_management/static/src/css/dashboard.css',
            'tickets_management/static/src/js/dashboard_action.js',
            'tickets_management/static/src/xml/dashboard_templates.xml',
        ],
    },

    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
