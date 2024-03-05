from . import emails  # Import the Blueprint you defined in flaskr/auth/__init__.py

@emails.route('/testing', methods=['POST']) 
def email():    
  return