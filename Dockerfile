# Use the official Python image for x86_64 architecture
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=mys.settings.production

# Set the working directory
WORKDIR /app

# Install dependencies
COPY mys/requirements.txt /app/
RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt

# Copy the project files
COPY mys /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Start the application
CMD ["gunicorn", "mys.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
