from app import create_app, db
from app.models import User, Department, IndentRequest, ApprovalLog, Rating

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Department=Department,
                IndentRequest=IndentRequest, ApprovalLog=ApprovalLog, Rating=Rating)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
