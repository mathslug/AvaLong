from flask import Flask, request, redirect, render_template, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from helpers import *
import re
import sys
from AvalonGame import AvalonGame

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
        if num_players not in [5, 6, 7, 8, 9, 10]:
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
    return redirect(url_for('game', game_id=game_id, player_name=username))

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
        return redirect(url_for('game', game_id=game_id, player_name=username))

@app.route('/avalom/game/<int:game_id>/<player_name>')
def game(game_id, player_name):
    game_info = games.get(game_id)
    if not game_info:
        return "Game not found", 404  # Return a 404 error if the game is not found

    if len(game_info['players']) < game_info["number_of_players"]:
        return redirect(url_for('game_waiting', game_id=game_id))
    elif not game_info.get("game_object"):
        game_info["game_object"] = AvalonGame(game_info['players'])
    
    this_game = game_info["game_object"]
    return redirect(url_for(this_game.mechanic_mode, game_id=game_id, player_name=player_name))

@app.route('/avalom/game_waiting/<int:game_id>')
def game_waiting(game_id):
    game_info = games.get(game_id)
    
    return render_markdown_template('game_waiting', {
        "game_id": str(game_id),
        "num_players": str(game_info["number_of_players"]),
        "player_list": ', '.join(game_info['players'])
    })

@app.route('/avalom/proposal/<int:game_id>/<player_name>')
def proposal(game_id, player_name):
    this_game = games.get(game_id).get("game_object")
    
    player_proposing = this_game.get_game_state()["current_turn"]
    if player_name != player_proposing:
        return render_markdown_template('proposal_off_turn', {
            "game_id": str(game_id),
            "turn_list": ', '.join(this_game.turn_order),
            "player_proposing": player_proposing,
            "player_name": player_name,
            "known_info": str(this_game.get_player_known_info(player_name)),
            "game_params": str(this_game.get_game_params()),
            "game_state": str(this_game.get_game_state()),
            "game_log": ' ~ '.join(this_game.log)
        })
    else:
        return render_template(
            'proposal_on_turn.html',
            game_id = str(game_id),
            turn_list = ', '.join(this_game.turn_order),
            player_list = this_game.turn_order,
            player_proposing = player_proposing,
            player_name = player_name,
            known_info = str(this_game.get_player_known_info(player_name)),
            game_params = str(this_game.get_game_params()),
            game_state = str(this_game.get_game_state()),
            game_log = ' ~ '.join(this_game.log)
        )

@app.route('/avalom/proposed_team/')
def proposed_team():
    selected_members = request.args.getlist('selectedItems')
    game_id = request.args.get('game_id')
    player_name = request.args.get('player_name')
    this_game = games.get(int(game_id)).get("game_object")
    mission_size = this_game.mission_participants[len(this_game.completed_missions)]

    if len(selected_members) == mission_size:
        this_game.propose_team(player_name, selected_members)
    
    return redirect(url_for(this_game.mechanic_mode, game_id=game_id, player_name=player_name))

@app.route('/avalom/voting/<int:game_id>/<player_name>')
def voting(game_id, player_name):
    this_game = games.get(game_id).get("game_object")
    proposed_team = this_game.proposed_team
    current_vote = this_game.votes.get(player_name)
    if current_vote is None:
        vote_string = "You have not voted"
    else:
        vote_string = f"You voted {'yes' if current_vote else 'no'}"
    return render_markdown_template('voting',{
        "game_id": str(game_id),
        "player_name": player_name,
        "proposed_team": ', '.join(proposed_team),
        "vote_string": vote_string,
        "known_info": str(this_game.get_player_known_info(player_name)),
        "game_params": str(this_game.get_game_params()),
        "game_state": str(this_game.get_game_state()),
        "game_log": ' ~ '.join(this_game.log)
    })

@app.route('/avalom/voting_result')
def voting_result():
    game_id = request.args.get('game_id')
    player_name = request.args.get('player_name')
    vote = request.args.get('vote') is not None and request.args.get('vote').lower() == "yes"
    this_game = games.get(int(game_id)).get("game_object")
    this_game.player_vote(player_name, vote)
    return redirect(url_for(this_game.mechanic_mode, game_id=game_id, player_name=player_name))

@app.route('/avalom/mission/<int:game_id>/<player_name>')
def mission(game_id, player_name):
    this_game = games.get(game_id).get("game_object")
    mission_team = this_game.get_game_state()["proposed_team"]
    current_action = this_game.mission_actions.get(player_name)
    if current_action is None:
        action_string = "You have not acted"
    else:
        action_string = f"You chose {'success' if current_action else 'sabotage'}"
    if player_name in mission_team:
        return render_markdown_template('mission_on_turn', {
            "game_id": str(game_id),
            "mission_team": ', '.join(this_game.proposed_team),
            "action_string": action_string,
            "player_name": player_name,
            "known_info": str(this_game.get_player_known_info(player_name)),
            "game_params": str(this_game.get_game_params()),
            "game_state": str(this_game.get_game_state()),
            "game_log": ' ~ '.join(this_game.log)
        })
    else:
        return render_markdown_template('mission_off_turn', {
            "game_id": str(game_id),
            "mission_team": ', '.join(this_game.proposed_team),
            "player_name": player_name,
            "known_info": str(this_game.get_player_known_info(player_name)),
            "game_params": str(this_game.get_game_params()),
            "game_state": str(this_game.get_game_state()),
            "game_log": ' ~ '.join(this_game.log)
        })

@app.route('/avalom/mission_action')
def mission_action():
    game_id = request.args.get('game_id')
    player_name = request.args.get('player_name')
    action = request.args.get('action') is not None and request.args.get('action').lower() == "succeed"
    this_game = games.get(int(game_id)).get("game_object")
    try:
        this_game.player_mission_act(player_name, action)
    except ValueError:
        pass
    return redirect(url_for(this_game.mechanic_mode, game_id=game_id, player_name=player_name))

@app.route('/avalom/ended/<int:game_id>/<player_name>')
def ended(game_id, player_name=None):
    this_game = games.get(game_id).get("game_object")
    return render_markdown_template('ended', {
        "game_id": str(game_id),
        "game_results": str(this_game.get_game_results()),
        "game_params": str(this_game.get_game_params()),
        "game_log": ' ~ '.join(this_game.log)
    })

@app.route('/avalom/assassination/<int:game_id>/<player_name>')
def assassination(game_id, player_name):
    this_game = games.get(game_id).get("game_object")
    assassin_player = [player for player, role in this_game.player_characters.items() if role ==  "Assassin"][0]
    if player_name != assassin_player:
        return render_markdown_template('assassination_off_turn', {
            "game_id": str(game_id),
            "assassin_player": assassin_player,
            "player_name": player_name,
            "known_info": str(this_game.get_player_known_info(player_name)),
            "game_params": str(this_game.get_game_params()),
            "game_state": str(this_game.get_game_state()),
            "game_log": ' ~ '.join(this_game.log)
        })
    else:
        return render_template(
            'assassination_on_turn.html',
            game_id = str(game_id),
            player_name = player_name,
            player_list = this_game.turn_order,
            known_info = str(this_game.get_player_known_info(player_name)),
            game_params = str(this_game.get_game_params()),
            game_state = str(this_game.get_game_state()),
            game_log = ' ~ '.join(this_game.log)
        )

@app.route('/avalom/assassination_selection')
def assassination_selection():
    game_id = request.args.get('game_id')
    player_name = request.args.get('player_name')
    target = request.args.get('selectedOption')
    this_game = games.get(int(game_id)).get("game_object")
    try:
        this_game.assassination(player_name, target)
    except ValueError:
        pass
    return redirect(url_for(this_game.mechanic_mode, game_id=game_id, player_name=player_name))


if __name__ == '__main__':
    app.run(debug='-d' in sys.argv or '--debug' in sys.argv)
