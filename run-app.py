# -*- coding: utf-8 -*-

from app import app
from waitress import serve


if __name__ == '__main__':
	serve(app, host='0.0.0.0', port=5000)
    # Running app in debug mode
    # app.run(debug=True)

