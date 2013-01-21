from webroot.game import Game

rooms = {

}

def get_smallest_game_id():
    next_id = len(rooms)
    if next_id == 0:
        create_new_game()

    smallest = min(rooms, key=lambda g: len(g.get_users()))
    return smallest.game_id

def create_new_game(game_id = None):
    if not game_id:
        game_id = len(rooms)
    game = Game(game_id, on_empty_game)
    rooms[game.game_id] = game
    return game

def get_or_create_room(game_id):
    try:
        game = rooms[game_id]
    except:
        game = create_new_game(game_id)
    return game

def on_empty_game(game_id):
    del rooms[game_id]