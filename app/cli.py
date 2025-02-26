import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import User, Patient, Doctor

@click.command('clear-users')
@with_appcontext
def clear_users_command():
    """Clear all users, patients, and doctors from the database."""
    try:
        # Delete in correct order to respect foreign key constraints
        Patient.query.delete()
        Doctor.query.delete()
        User.query.delete()
        db.session.commit()
        click.echo('Successfully cleared all users.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error clearing users: {str(e)}') 