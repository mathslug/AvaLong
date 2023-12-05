# Mission Time

**Game ID:** {{ game_id }}

**{{ mission_team }}** are going on a mission

{{ action_string }}. Take or revise your action below.

<form action="/avalom/mission_action" method="get">
    <input type="hidden" name="game_id" value="{{ game_id }}">
    <input type="hidden" name="player_name" value="{{ player_name }}">

    <label>
        <input type="radio" name="action" value="succeed">
        Succeed
    </label>
    <label>
        <input type="radio" name="action" value="sabotage">
        Sabotage
    </label>
    <br>
    <input type="submit" value="Submit Action">
</form>

The game will proceed once everyone has acted.

## Your Info

Your name is {{ player_name }}. Here's your game info:

{{ known_info }}

## Game State

{{ game_state }}

## Game Parameters

{{ game_params }}

## Game Log

{{ game_log }}
