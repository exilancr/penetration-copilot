

from flask import Flask
# from flask import current_app
import markdown
from pydantic import BaseModel

def contact_to_html(contact):
    formatters = {
        "email": lambda c: f'<i class="fa-solid fa-envelope"></i>&nbsp;<a class="mimic" href="mailto:{c.value}">{c.value}</a>',
        "phone": lambda c: f'<i class="fa-solid fa-square-phone"></i>&nbsp;<a class="mimic" href="tel:{c.value}">{c.value}</a>',
        "linkedin": lambda c: f'<i class="fa-brands fa-linkedin"></i>&nbsp;<a class="mimic" href="https://linkedin.com/in/{c.value}">{c.value}</a>',
        "github": lambda c: f'<i class="fa-brands fa-github"></i>&nbsp;<a class="mimic" href="https://github.com/{c.value}">{c.value}</a>',
        "location": lambda c: f'<i class="fa-solid fa-map-marker-alt"></i>&nbsp;{c.value}',
    }
    return formatters.get(contact.type, lambda c: c.value)(contact)

def markdown_to_html(input):
    return markdown.markdown(input)

def pydantic_to_json(input: BaseModel, indent=4):
    return input.model_dump_json(indent=indent)

def safe_date(date):
    return date.strftime("%Y-%m-%d") if date else "NONE"

def register_formatters(app: Flask):
    app.jinja_env.filters["contact"] = contact_to_html
    app.jinja_env.filters["markdown"] = markdown_to_html
    app.jinja_env.filters["pydantic_to_json"] = pydantic_to_json
    app.jinja_env.filters["safe_date"] = safe_date