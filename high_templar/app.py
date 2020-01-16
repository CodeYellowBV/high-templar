if __name__ == '__main__':
    from main import create_app

    class Config:
        def __init__(self):
            self.API_URL = 'foo/bar'

    app = create_app(Config())

    # Don't change from multithreaded to multiprocess. It will brick the server (wtf)
    app.run(host="0.0.0.0", threaded=False, port=8000, processes=3, debug=True)
