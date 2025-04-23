# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../..')) # Point to project root

# -- Project information -----------------------------------------------------
project = 'pipmaster'
copyright = '2024-2025, ParisNeo'
author = 'ParisNeo'

# Get version from package
try:
    from pipmaster import __version__ as release
except ImportError:
    release = '0.7.0' # Fallback

version = '.'.join(release.split('.')[:2]) # The short X.Y version

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Core library for html generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables
    'sphinx.ext.napoleon',     # Support for NumPy and Google style docstrings
    'sphinx.ext.intersphinx',  # Link to other projects' documentation (e.g. Python)
    'sphinx.ext.viewcode',     # Add links to source code
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Autodoc settings
autodoc_member_order = 'bysource'
# autodoc_typehints = 'description' # Show typehints in description, not signature
# napoleon_google_docstring = True
# napoleon_numpy_docstring = False

# Intersphinx mapping
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}


# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme' # Read the Docs theme
html_static_path = ['_static']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']