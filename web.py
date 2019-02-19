from flask import Flask
from flask import request

import index

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello():
	if 'challenge' in request.json:
		return request.json['challenge']

	command, channel = index.parse_bot_commands([request.json['event']])
	if command:
		index.handle_command(command, channel)
	return 'blah'

if __name__ == '__main__':
	app.run(debug=True)