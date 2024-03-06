import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from auth import auth
from api import api
from handleEmails import emails

from background import AuditNotifier
from threading import Thread

app = Flask(__name__)
CORS(app)

def create_app():
    """Application factory function to create and configure the Flask app."""


    ###### TAKE COMMENTS OUT OF BELOW 4 LINES TO START THE EMAIL CHECKER ########
    # audit_notifier = AuditNotifier()  # Assuming you need to instantiate it
    # thread = Thread(target=audit_notifier.run)
    # thread.daemon = True  # Optionally make it a daemon thread
    # thread.start()

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.register_blueprint(auth, url_prefix='/auth')

    app.register_blueprint(api, url_prefix='/api')

    app.register_blueprint(emails, url_prefix='/emails')

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Sample route
    @app.route('/api/postdata', methods=['POST'])
    def post_data():
        data = request.json
        print(data)
        return jsonify({'status': 'Data received'})

    CORS(app, origins=["https://yourfrontend.com", "http://lt-mbrandow:3000", "http://localhost:3000"])


    return app

# Adjust this part of your code
# if __name__ == '__main__':
#     app = create_app()  # Use the factory function to create the app
#     if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
#         audit_notifier = AuditNotifier()  # Assuming you need to instantiate it
#         thread = Thread(target=audit_notifier.run)
#         thread.daemon = True  # Optionally make it a daemon thread
#         thread.start()
#     app.run(debug=True)