"""
Application package for the backend FastAPI service.

Subpackages:
- api:      API route definitions
- core:     configuration, security, and shared utilities
- models:   database models
- services: domain services (matching, resume parsing, scheduler)
- integrations: job board integrations
- workers:  background task queue + Celery tasks
- db:       database session and initialization helpers
"""

