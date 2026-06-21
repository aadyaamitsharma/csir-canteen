from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models import IndentRequest, ApprovalLog
from datetime import datetime

print_bp = Blueprint('print_bp', __name__)

@print_bp.route('/indent/print/<int:id>')
@login_required
def print_indent(id):
    indent = IndentRequest.query.get_or_404(id)

    # Access control — each role can only print what they're allowed to see
    if current_user.role == 'indentor':
        if indent.indentor_id != current_user.id:
            abort(403)

    elif current_user.role == 'hod':
        if indent.department_id != current_user.department_id:
            abort(403)

    elif current_user.role in ['chairman', 'manager', 'admin']:
        pass  # Can print any indent

    else:
        abort(403)

    logs = ApprovalLog.query.filter_by(indent_id=id).order_by(ApprovalLog.timestamp).all()
    now = datetime.now()

    return render_template('shared/print_indent.html', indent=indent, logs=logs, now=now)
