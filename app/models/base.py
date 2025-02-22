from datetime import datetime
from app import db

class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CRUDMixin:
    """Mixin that adds convenience methods for CRUD operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()

class Model(db.Model, CRUDMixin):
    """Base model class that includes CRUD convenience methods."""
    __abstract__ = True

class PaginatedMixin:
    """Mixin to add pagination capabilities to models."""
    
    @classmethod
    def paginate(cls, page=1, per_page=20, *args, **kwargs):
        """Return a paginated result."""
        return cls.query.filter(*args).paginate(
            page=page, per_page=per_page, error_out=False
        ) 