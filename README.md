# Supervisor Workers Agent

A FastAPI application with Jinja2 templating support for serving dynamic HTML pages alongside RESTful API endpoints.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 📄 **Jinja2 Templates** - Dynamic HTML page rendering with template inheritance
- 🎨 **Static Files** - Support for CSS, JavaScript, and other static assets
- 📡 **API & HTML** - Serve both API endpoints and HTML pages from the same application
- 🔄 **Hot Reload** - Automatic reload during development

## Project Structure

```
supervisor-workers-agent/
├── main.py              # FastAPI application entry point
├── templates/           # Jinja2 HTML templates
│   ├── base.html       # Base template with common layout
│   ├── index.html      # Home page
│   └── about.html      # About page
├── static/             # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css   # Main stylesheet
│   └── js/             # JavaScript files
├── pyproject.toml      # Project dependencies
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.12 or higher
- uv (recommended) or pip

### Setup

1. **Clone or navigate to the project directory**

2. **Install dependencies using uv (recommended):**
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

## Running the Application

### Method 1: Using Python directly

```bash
python main.py
```

### Method 2: Using uvicorn

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Home page**: http://localhost:8000
- **About page**: http://localhost:8000/about
- **API docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)

## Available Endpoints

### HTML Pages
- `GET /` - Home page
- `GET /about` - About page

### API Endpoints
- `GET /api/health` - Health check endpoint (returns JSON)
- `GET /api/data` - Sample data endpoint (returns JSON)

## Development

### Adding New Pages

1. **Create a new template** in `templates/`:
   ```html
   {% extends "base.html" %}
   
   {% block content %}
   <h1>Your Page Title</h1>
   <p>Your content here</p>
   {% endblock %}
   ```

2. **Add a route** in `main.py`:
   ```python
   @app.get("/your-page", response_class=HTMLResponse)
   async def your_page(request: Request):
       return templates.TemplateResponse(
           "your_page.html",
           {"request": request, "title": "Your Page"}
       )
   ```

### Adding API Endpoints

```python
@app.get("/api/your-endpoint")
async def your_endpoint():
    return {"message": "Your data here"}
```

### Adding Static Files

Place your static files in the appropriate directory:
- CSS files: `static/css/`
- JavaScript files: `static/js/`
- Images: `static/images/`

Reference them in templates:
```html
<link rel="stylesheet" href="{{ url_for('static', path='/css/your-style.css') }}">
<script src="{{ url_for('static', path='/js/your-script.js') }}"></script>
```

## Template System

This project uses Jinja2 for templating. The `base.html` template provides:
- Common HTML structure
- Navigation bar
- Footer
- CSS and JavaScript inclusion
- Block system for content extension

### Template Blocks

- `{% block title %}` - Page title
- `{% block extra_css %}` - Additional CSS files
- `{% block content %}` - Main page content
- `{% block extra_js %}` - Additional JavaScript files

## Dependencies

- **fastapi** - Web framework
- **uvicorn[standard]** - ASGI server
- **jinja2** - Template engine
- **python-multipart** - Form data support

## License

This project is open source and available under the MIT License.

## Next Steps

- Add database integration (SQLAlchemy, MongoDB, etc.)
- Implement user authentication
- Add form handling with validation
- Implement HTMX for dynamic updates
- Add more API endpoints
- Set up testing with pytest
- Deploy to production (Docker, cloud platforms)
