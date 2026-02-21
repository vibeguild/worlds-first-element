#!/usr/bin/env python3
"""
🏛️ TEMPLE OF FORTUNES 🏛️
A mystical roguelike adventure

Created by the Vibe Guild team:
- aria (Team Leader) - Vision & fortune mechanics  
- blake (Team Member) - Game logic & combat system

Navigate through ancient chambers, collect fortune scrolls,
defeat temple guardians, and discover the legendary Oracle!
"""

import random
import json
import os
import sys
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# FORTUNE SCROLLS - Cryptic wisdom found throughout the temple
# ═══════════════════════════════════════════════════════════════

FORTUNES = {
    "wisdom": [
        "📜 'The path forward is never straight, but always true.'",
        "📜 'Wealth measured in gold is poverty of spirit.'",
        "📜 'The mightiest warrior is the one who knows when to rest.'",
        "📜 'Every ending is a doorway in disguise.'",
        "📜 'Fear speaks loudly, but courage whispers first.'",
    ],
    "prophecy": [
        "📜 'A guardian awaits where shadows deepen...'",
        "📜 'The Oracle's chamber lies beyond the fifth gate.'",
        "📜 'Three potions shall save you from final darkness.'",
        "📜 'The treasure you seek also seeks you.'",
        "📜 'Beware the friendly face in room seven.'",
    ],
    "humor": [
        "📜 'You will find gold. You will also lose it. Such is life.'",
        "📜 'A slime considers you very attractive. Run.'",
        "📜 'The temple architect had... interesting ideas.'",
        "📜 'Help wanted: Temple guardian. Must not fear adventurers.'",
        "📜 'Your fortune: \//\//\\//\\/ Good luck reading this.'",
    ],
    "cryptic": [
        "📜 'OXOXL XOX OXOXOXO... the inscription fades.'",
        "📜 'When north is south and up is down, seek the center.'",
        "📜 'The number you need is not a number.'",
        "📜 'Left feels right today. Or does right feel left?'",
        "📜 '...and that is why you should always bring a towel.'",
    ]
}

# ═══════════════════════════════════════════════════════════════
# ASCII ART - Visual elements for immersion
# ═══════════════════════════════════════════════════════════════

TITLE_ART = '''
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║     ███████╗████████╗██╗   ██╗███████╗██████╗        ║
║     ██╔════╝╚══██╔══╝██║   ██║██╔════╝██╔══██╗       ║
║     █████╗     ██║   ██║   ██║█████╗  ██████╔╝       ║
║     ██╔══╝     ██║   ╚██╗ ██╔╝██╔══╝  ██╔══██╗       ║
║     ██║        ██║    ╚████╔╝ ███████╗██║  ██║       ║
║     ╚═╝        ╚═╝     ╚═══╝  ╚══════╝╚═╝  ╚═╝       ║
║                                                       ║
║        ██████╗  █████╗ ███╗   ██╗███████╗            ║
║        ██╔══██╗██╔══██╗████╗  ██║██╔════╝            ║
║        ██████╔╝███████║██╔██╗ ██║█████╗              ║
║        ██╔══██╗██╔══██║██║╚██╗██║██╔══╝              ║
║        ██████╔╝██║  ██║██║ ╚████║███████╗            ║
║        ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝            ║
║                                                       ║
║            ~ A Mystical Roguelike Adventure ~         ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
'''

PLAYER_ART = '''
    ⚔️
   /|\
   / \
'''

MONSTERS = {
    "Temple Slime": '''
   ~~~
  (o.o)
   ~~~
''',
    "Stone Guardian": '''
   .---.
  / o o \
  |  ^  |
   \_-_/ 
    | |
   /   \
''',
    "Shadow Wraith": '''
   .-.
  (o o)
  | ~ |
   \|/
   / \
''',
    "Temple Oracle": '''
   .---.
  / \*/ \
  | ~~~ |
  \_____/
   ~| |~
    | |
'''
}

# ═══════════════════════════════════════════════════════════════
# GAME CLASSES
# ═══════════════════════════════════════════════════════════════

class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.attack = 15
        self.defense = 5
        self.gold = 0
        self.potions = 2
        self.scrolls_collected = []
        self.rooms_explored = 0
        self.x = 0
        self.y = 0
    
    def heal(self, amount):
        healed = min(amount, self.max_hp - self.hp)
        self.hp += healed
        return healed
    
    def take_damage(self, amount):
        actual = max(1, amount - self.defense)
        self.hp -= actual
        return actual
    
    def is_alive(self):
        return self.hp > 0

class Monster:
    def __init__(self, name, hp, attack, gold_reward, art):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.gold_reward = gold_reward
        self.art = art
    
    def take_damage(self, amount):
        self.hp -= amount
        return amount
    
    def is_alive(self):
        return self.hp > 0

class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.explored = False
        self.has_scroll = random.random() < 0.4
        self.scroll_type = random.choice(list(FORTUNES.keys()))
        self.has_potion = random.random() < 0.2
        self.has_gold = random.random() < 0.5
        self.gold_amount = random.randint(5, 25)
        self.monster = None
        self.is_oracle_chamber = False
        
        # Spawn monsters based on distance from start
        monster_chance = min(0.6, 0.2 + (abs(x) + abs(y)) * 0.05)
        if random.random() < monster_chance and not self.is_oracle_chamber:
            self.spawn_monster()
    
    def spawn_monster(self):
        monsters = [
            ("Temple Slime", 20, 8, 10, MONSTERS["Temple Slime"]),
            ("Stone Guardian", 35, 12, 20, MONSTERS["Stone Guardian"]),
            ("Shadow Wraith", 45, 18, 35, MONSTERS["Shadow Wraith"]),
        ]
        # Harder monsters further from center
        difficulty = min(2, (abs(self.x) + abs(self.y)) // 3)
        name, hp, atk, gold, art = monsters[difficulty]
        self.monster = Monster(name, hp, atk, gold, art)

class Temple:
    def __init__(self):
        self.rooms = {}
        self.oracle_x = random.choice([-5, 5])
        self.oracle_y = random.choice([-5, 5])
    
    def get_room(self, x, y):
        key = (x, y)
        if key not in self.rooms:
            room = Room(x, y)
            if x == self.oracle_x and y == self.oracle_y:
                room.is_oracle_chamber = True
                room.monster = Monster("Temple Oracle", 80, 25, 100, MONSTERS["Temple Oracle"])
                room.has_scroll = True
                room.scroll_type = "wisdom"
            self.rooms[key] = room
        return self.rooms[key]

# ═══════════════════════════════════════════════════════════════
# GAME FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_slow(text, delay=0.02):
    for char in text:
        print(char, end='', flush=True)
        time_delay(delay)
    print()

def time_delay(seconds):
    import time
    time.sleep(seconds)

def display_status(player):
    print("\n" + "═" * 50)
    print(f"  ⚔️ {player.name} the Adventurer")
    print(f"  ❤️ HP: {player.hp}/{player.max_hp}")
    print(f"  💰 Gold: {player.gold}")
    print(f"  🧪 Potions: {player.potions}")
    print(f"  📜 Scrolls: {len(player.scrolls_collected)}")
    print(f"  🗺️ Location: ({player.x}, {player.y})")
    print("═" * 50)

def display_minimap(player, temple):
    print("\n  🗺️ TEMPLE MAP:")
    print("  ┌───────────┐")
    for y in range(3, -4, -1):
        row = "  │"
        for x in range(-3, 4):
            if x == player.x and y == player.y:
                row += "@"
            elif (x, y) in temple.rooms and temple.rooms[(x, y)].explored:
                room = temple.rooms[(x, y)]
                if room.is_oracle_chamber:
                    row += "★"
                elif room.monster and room.monster.is_alive():
                    row += "!"
                else:
                    row += "."
            else:
                row += " "
        row += "│"
        print(row)
    print("  └───────────┘")
    print("  @ = You  ! = Monster  ★ = Oracle  . = Explored")

def get_random_scroll(scroll_type):
    scrolls = FORTUNES.get(scroll_type, FORTUNES["wisdom"])
    return random.choice(scrolls)

def combat(player, monster):
    print(f"\n⚔️ A {monster.name} blocks your path!")
    print(monster.art)
    
    while player.is_alive() and monster.is_alive():
        print(f"\n  You: {player.hp}HP | {monster.name}: {monster.hp}HP")
        print("  [A]ttack [D]efend [H]eal [F]lee")
        
        action = input("  Choice: ").lower().strip()
        
        if action == 'a':
            damage = player.attack + random.randint(-3, 5)
            monster.take_damage(damage)
            print(f"  You strike for {damage} damage!")
            
            if monster.is_alive():
                enemy_damage = monster.attack + random.randint(-2, 4)
                player.take_damage(enemy_damage)
                print(f"  {monster.name} retaliates for {enemy_damage} damage!")
        
        elif action == 'd':
            enemy_damage = max(0, monster.attack - player.defense - 5)
            player.take_damage(enemy_damage)
            print(f"  You block! {monster.name} only deals {enemy_damage} damage.")
        
        elif action == 'h':
            if player.potions > 0:
                player.potions -= 1
                healed = player.heal(30)
                print(f"  You drink a potion and restore {healed} HP!")
            else:
                print("  No potions left!")
        
        elif action == 'f':
            if random.random() < 0.5:
                print("  You escape successfully!")
                return "fled"
            else:
                print("  Can't escape!")
                enemy_damage = monster.attack
                player.take_damage(enemy_damage)
                print(f"  {monster.name} strikes as you flee for {enemy_damage} damage!")
    
    if player.is_alive():
        player.gold += monster.gold_reward
        print(f"\n  🎉 Victory! You gained {monster.gold_reward} gold!")
        return "won"
    else:
        return "died"

def explore_room(player, room):
    room.explored = True
    player.rooms_explored += 1
    
    print(f"\n  Entering chamber at ({room.x}, {room.y})...")
    
    # Check for treasure
    if room.has_gold and not room.monster:
        print(f"  💰 You found {room.gold_amount} gold!")
        player.gold += room.gold_amount
        room.has_gold = False
    
    if room.has_potion and not room.monster:
        print("  🧪 You found a healing potion!")
        player.potions += 1
        room.has_potion = False
    
    # Combat if monster present
    if room.monster and room.monster.is_alive():
        if room.is_oracle_chamber:
            print("  ✨ The air shimmers with ancient power...")
            print("  A mystical voice echoes: 'You have found me at last...'")
        
        result = combat(player, room.monster)
        
        if result == "died":
            return False
        elif result == "fled":
            return True
    
    # Collect scroll after combat
    if room.has_scroll and room.scroll_type:
        scroll = get_random_scroll(room.scroll_type)
        print(f"\n  {scroll}")
        player.scrolls_collected.append(scroll)
        room.has_scroll = False
    
    # Check for Oracle victory
    if room.is_oracle_chamber and not room.monster.is_alive():
        print("\n" + "═" * 50)
        print("  🌟 THE ORACLE SPEAKS 🌟")
        print("  'Brave adventurer, you have proven worthy!'")
        print("  'The temple's treasures are now yours.'")
        print("  'But remember: the greatest fortune is the journey itself.'")
        print("═" * 50)
        print("\n  🏆 CONGRATULATIONS! YOU WIN! 🏆")
        print(f"  Final Stats: {player.gold} gold, {len(player.scrolls_collected)} scrolls")
        return "victory"
    
    return True

def save_game(player, temple):
    data = {
        "player": {
            "name": player.name,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "attack": player.attack,
            "defense": player.defense,
            "gold": player.gold,
            "potions": player.potions,
            "scrolls_collected": player.scrolls_collected,
            "rooms_explored": player.rooms_explored,
            "x": player.x,
            "y": player.y
        },
        "temple": {
            "oracle_x": temple.oracle_x,
            "oracle_y": temple.oracle_y,
            "explored_rooms": [(k[0], k[1], v.explored) for k, v in temple.rooms.items() if v.explored]
        },
        "saved_at": datetime.now().isoformat()
    }
    
    with open("temple_save.json", "w") as f:
        json.dump(data, f, indent=2)
    print("  💾 Game saved!")

def load_game():
    try:
        with open("temple_save.json", "r") as f:
            data = json.load(f)
        
        p = data["player"]
        player = Player(p["name"])
        player.hp = p["hp"]
        player.max_hp = p["max_hp"]
        player.attack = p["attack"]
        player.defense = p["defense"]
        player.gold = p["gold"]
        player.potions = p["potions"]
        player.scrolls_collected = p["scrolls_collected"]
        player.rooms_explored = p["rooms_explored"]
        player.x = p["x"]
        player.y = p["y"]
        
        t = data["temple"]
        temple = Temple()
        temple.oracle_x = t["oracle_x"]
        temple.oracle_y = t["oracle_y"]
        
        for x, y, explored in t.get("explored_rooms", []):
            room = temple.get_room(x, y)
            room.explored = explored
        
        return player, temple
    except FileNotFoundError:
        return None, None

def game_loop():
    clear_screen()
    print(TITLE_ART)
    print("  Created by the Vibe Guild")
    print("  aria (Team Leader) & blake (Team Member)")
    print()
    
    print("  [N]ew Game  [L]oad Game  [Q]uit")
    choice = input("  Choice: ").lower().strip()
    
    if choice == 'q':
        print("  Farewell, adventurer!")
        return
    
    if choice == 'l':
        player, temple = load_game()
        if player is None:
            print("  No save file found. Starting new game...")
            choice = 'n'
    
    if choice == 'n':
        name = input("  Enter your name, adventurer: ").strip() or "Wanderer"
        player = Player(name)
        temple = Temple()
        
        print(f"\n  Welcome, {name}!")
        print("  You stand at the entrance of the Temple of Fortunes.")
        print("  Legend speaks of an Oracle who grants infinite wisdom...")
        print("  But beware - the temple is filled with guardians!")
    
    # Main game loop
    while player.is_alive():
        clear_screen()
        display_status(player)
        display_minimap(player, temple)
        
        current_room = temple.get_room(player.x, player.y)
        
        print("\n  [N]orth [S]outh [E]ast [W]est [R]est [M]ap [V]iew Scrolls [Save] [Quit]")
        
        if not current_room.explored:
            result = explore_room(player, current_room)
            if result == "victory":
                break
            elif result == False:
                print("\n  💀 You have fallen in the Temple of Fortunes...")
                print("  But fortune favors the bold. Try again!")
                break
            input("\n  Press Enter to continue...")
            continue
        
        action = input("  Choice: ").lower().strip()
        
        if action == 'n':
            player.y += 1
        elif action == 's':
            player.y -= 1
        elif action == 'e':
            player.x += 1
        elif action == 'w':
            player.x -= 1
        elif action == 'r':
            if player.hp < player.max_hp:
                heal = player.heal(10)
                print(f"  You rest and recover {heal} HP.")
            else:
                print("  You're already at full health!")
            input("  Press Enter to continue...")
        elif action == 'm':
            display_minimap(player, temple)
            input("  Press Enter to continue...")
        elif action == 'v':
            print("\n  📜 YOUR SCROLL COLLECTION:")
            if player.scrolls_collected:
                for scroll in player.scrolls_collected:
                    print(f"    {scroll}")
            else:
                print("    No scrolls collected yet!")
            input("\n  Press Enter to continue...")
        elif action == 'save':
            save_game(player, temple)
            input("  Press Enter to continue...")
        elif action == 'quit' or action == 'q':
            print("  Until we meet again, adventurer!")
            break

if __name__ == "__main__":
    game_loop()
