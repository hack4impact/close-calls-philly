import csv
import datetime
from ..decorators import admin_required
from flask import (
    render_template,
    abort,
    redirect,
    flash,
    url_for,
    request,
    Response,
)
from flask_login import login_required, current_user
from flask_rq import get_queue
from .forms import (
    ChangeUserEmailForm,
    ChangeUserPhoneNumberForm,
    ChangeAccountTypeForm,
    InviteUserForm,
)
from . import admin
from ..models import User, Role, EditableHTML, Incident, IncidentLocation
from .. import db
from ..utils import parse_phone_number, url_for_external
from ..email import send_email


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(role=form.role.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    phone_number=parse_phone_number(form.phone_number.data))

        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for_external('account.join_from_invite',
                                       user_id=user.id, token=token)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link,
        )
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
        return redirect(url_for('admin.invite_user'))
    return render_template('admin/invite_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/registered_users.html', users=users,
                           roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'
              .format(user.full_name(), user.email),
              'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/change-phone-number',
             methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_phone_number(user_id):
    """Change a user's phone number."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserPhoneNumberForm()
    if form.validate_on_submit():
        user.phone_number = parse_phone_number(form.phone_number.data)
        db.session.add(user)
        db.session.commit()
        flash('Phone number for user {} successfully changed to {}.'
              .format(user.full_name(), user.phone_number),
              'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/change-account-type',
             methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'
              .format(user.full_name(), user.role.name),
              'form-success')
    form.role.default = user.role
    form.process()
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.get_editable_html(editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200


@admin.route('/download_reports', methods=['GET'])
@login_required
@admin_required
def download_reports():
    """Download a csv file of all incident reports."""

    def encode(s):
        return s.encode('utf-8') if s else ''

    current_date = str(datetime.date.today())
    csv_name = 'Incidents-' + current_date + '.csv'
    outfile = open(csv_name, 'w+')
    print('initial file contents:', outfile.read())

    wr = csv.writer(outfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    reports = db.session.query(Incident).all()
    wr.writerow(['DATE', 'LOCATION', 'VEHICLE ID', 'DURATION',
                'LICENSE PLATE', 'DESCRIPTION'])
    for r in reports:
        wr.writerow([r.date, r.location,
                     r.vehicle_id, r.duration,
                     r.license_plate, encode(r.description)])

    endfile = open(csv_name, 'r+')
    data = endfile.read()
    return Response(
        data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=" + csv_name})
