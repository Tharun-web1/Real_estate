import os
import sys
from importlib.util import spec_from_file_location, module_from_spec

# Add your project directory to sys.path
project_dir = os.path.dirname(__file__)
sys.path.insert(0, project_dir)

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "properties.settings")

# Load Django WSGI application

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
 


