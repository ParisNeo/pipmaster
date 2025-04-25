# docs/conf.py
# -*- coding: utf-8 -*-
import os
import sys
# Point to project root (assuming docs/ is one level inside project)
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'pipmaster'
copyright = '2024-2025, ParisNeo'
author = 'ParisNeo'

# Get version from package
try:
    from pipmaster import __version__ as release
except ImportError:
    # Fallback if package not installed or during early build stages
    # Read from pyproject.toml or hardcode temporarily if necessary
    release = '0.7.0' # Ensure this matches your intended release

version = '.'.join(release.split('.')[:2]) # The short X.Y version

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Core library for html generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables
    'sphinx.ext.napoleon',     # Support for NumPy and Google style docstrings
    'sphinx.ext.intersphinx',  # Link to other projects' documentation
    'sphinx.ext.viewcode',     # Add links to source code
    'sphinx.ext.githubpages', # Helps with GitHub Pages deployment paths
    'myst_parser',             # To include Markdown files like README
]

# Autosummary settings
autosummary_generate = True  # Turn on automatic generation of stub files
# Optional: Add templates for autosummary if needed
# autosummary_context = {}
# autosummary_imported_members = True

# Napoleon settings (if using Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True # Or False, depending on your style
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_autosummary_sync/*', '_autosummary_async/*'] # Ignore generated files

# The master toctree document.
master_doc = 'index' # Changed from root_doc for older Sphinx compatibility if needed

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme' # Read the Docs theme
# html_logo = "_static/logo.png" # Optional: Add your logo file here
# html_favicon = "_static/favicon.ico" # Optional: Add your favicon here

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# If you have custom CSS:
# html_css_files = ['css/custom.css']

# Intersphinx mapping for linking to other docs
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'packaging': ('https://packaging.pypa.io/en/latest/', None),
    'asyncio': ('https://docs.python.org/3/library/asyncio.html', None),
}

# MyST Parser Settings (if using Markdown files)
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]
myst_url_schemes = ("http", "https", "mailto")
# If including README.md from root
# source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown'}

# Autodoc settings
autodoc_member_order = 'bysource' # Order members by source order
autodoc_typehints = 'signature' # Show typehints in signature, not description
autodoc_preserve_defaults = True # Preserve default values in signatures