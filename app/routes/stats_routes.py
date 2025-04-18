def init_stats_routes(app):
    @app.route('/stats', methods=['GET'])
    def stats():
        # Handle stats logic here
        return "Stats Page"