from app import application

@application.route('/main', methods=['GET'])
def main():
    # Handle main logic here
    return "Main Page"