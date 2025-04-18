def init_main_routes(app):
    @app.route('/main', methods=['GET'])
    def main():
        # Handle main logic here
        return "Main Page"