from app import application

@application.route('/login', methods=['GET', 'POST'])
def login():
    # Handle login logic here
    return "Login Page"

@application.route('/register', methods=['GET', 'POST'])
def register():
    # Handle registration logic here
    return "Register Page"

