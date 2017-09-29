import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('..'))
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo', 'sphinx.ext.coverage',
              'sphinx.ext.mathjax', 'sphinx.ext.viewcode']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'IMPLib2'
year = datetime.now().year
copyright = u'%d Markus Hubig' % year

exclude_patterns = ['_build']

html_theme = 'alabaster'
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ]
}
html_theme_options = {
    'description': 'Python implementation of the IMPBUS-2 protocol.',
    'sidebar_collapse': False,
    'page_width': '1000px',
    'code_font_size': '0.8em',
    'github_user': 'mhubig',
    'github_repo': 'implib2',
    'github_button': False,
    'github_banner': True,
    'fixed_sidebar': True,
}
