from flask import Flask, request, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from helpers import *
import re
import sys

app = Flask(__name__)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour", "4 per second"],
    # I should change the below if I care about performance or multiple nodes
    storage_uri="memory://" 
)

games = {}

@app.route('/')
def meta_home():
    return redirect(url_for('home'))

@app.route('/avalom/')
def home():
    return render_markdown_template('home')

@app.route('/avalom/create_game')
def create_game():
    username = request.args.get('username', '').strip()
    num_players = request.args.get('num_players', '').strip()

    # username may contain only letters, may not be empty
    if not username or not re.match("^[A-Za-z]+$", username):
        return redirect(url_for('home'))
    
    try:
        num_players = int(num_players)
        if num_players not in [6, 7, 8, 9]:
            raise ValueError("Invalid number of players.")
    except ValueError:
        return redirect(url_for('home'))

    # Find the lowest positive integer not already used as a key
    game_id = min(set(range(1, len(games) + 2)) - set(games.keys()))

    # Create a new game entry
    games[game_id] = {
        'number_of_players': num_players,
        'players': [username]
    }

    # Redirect to the game page
    return redirect(url_for('game', game_id=game_id))

@app.route('/avalom/join_game')
def join_game():
    username = request.args.get('username', '').strip()
    game_id = request.args.get('game_id', '').strip()

    # username may contain only letters, may not be empty
    if not username or not re.match("^[A-Za-z]+$", username):
        return redirect(url_for('home'))

    try:
        game_id = int(game_id)
        if game_id not in games:
            raise ValueError("Invalid game ID")
    except ValueError:
        # Redirect back to home if invalid game ID
        return redirect(url_for('home'))

    game = games[game_id]

    # Check if the user is not already in the game and if there is room
    if username not in game['players'] and len(game['players']) < game['number_of_players']:
        game['players'].append(username)

    # Redirect to the game page only if the user is in the players list
    if username not in game['players']:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('game', game_id=game_id))

@app.route('/avalom/game/<int:game_id>')  # Define the route with a dynamic segment
def game(game_id):
    game_info = games.get(game_id)
    if not game_info:
        return "Game not found", 404  # Return a 404 error if the game is not found

    # Render a template to display game info (or directly return it for now)
    return f"Game ID: {game_id}, Info: {game_info}"

if __name__ == '__main__':
    app.run(debug='-d' in sys.argv or '--debug' in sys.argv)
