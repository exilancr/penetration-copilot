

from flask import current_app
from jinja2 import Environment, PackageLoader, select_autoescape

# env = Environment(
#     loader=PackageLoader("copilot"),
#     autoescape=select_autoescape()
# )


def register_views(app):
    app.jinja_env.loader = PackageLoader("copilot")


def render_page(name: str, **kwargs):
    template = current_app.jinja_env.get_template(name)
    return template.render(**kwargs)





