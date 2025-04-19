from app import application

@application.route('/stats', methods=['GET'])
def stats():
    # Handle stats logic here
    return "Stats Page"