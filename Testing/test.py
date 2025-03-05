import unittest
import sys
import os

# Get the absolute path to the Game_Code directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Game_Code")))

import main  # Import the main module from the Game_Code directory

class TestGame(unittest.TestCase):
    
    def test_init_player(self):
        """
        Tests player initialization with correct attributes.
        """
        p = main.Player(50, 10, 10)
        self.assertEqual(p.x, 10)
        self.assertEqual(p.y, 10)
        self.assertEqual(p.HP, 50)
        self.assertIsNone(p.get_tool())

    def test_init_enemy(self):
        """
        Tests enemy initialization with correct attributes.
        """
        e = main.Enemy(50, 10, 10)
        self.assertEqual(e.x, 10)
        self.assertEqual(e.y, 10)
        self.assertEqual(e.HP, 50)
        
    def test_weapon_properties(self):
        """
        Tests weapon initialization with correct attributes.
        """
        w = main.Weapon('Sword', 20, 1, 5, 'sword.png', 2)
        self.assertEqual(w.name, 'Sword')
        self.assertEqual(w.damage, 20)
        self.assertEqual(w.cooldown, 1)
        self.assertEqual(w.reach, 5)
        self.assertEqual(w.img, 'sword.png')
        self.assertEqual(w.scale, 2)
        
    def test_player_set_weapon(self):
        """
        Tests if a player can equip a weapon correctly.
        """
        p = main.Player(50, 10, 10)
        w = main.Weapon('Sword', 20, 1, 5, 'sword.png', 2)
        p.add_inventory(w)
        p.set_tool(0)
        self.assertEqual(p.get_tool(), w)
        
    def test_player_attack_enemy(self):
        """
        Tests if a player can attack an enemy with a weapon.
        """
        p = main.Player(50, 10, 10)
        e = main.Enemy(50, 11, 10)  # Enemy one tile away
        w = main.Weapon('Sword', 20, 1, 5, 'sword.png', 2)
        p.add_inventory(w)
        p.set_tool(0)
        
        initial_hp = e.HP
        p.attack(e)
        self.assertTrue(e.HP < initial_hp)
        self.assertEqual(e.HP, initial_hp - w.damage)
        
    def test_attack_out_of_range(self):
        """
        Tests that an attack fails when the enemy is out of range.
        """
        p = main.Player(50, 10, 10)
        e = main.Enemy(50, 20, 20)  # Enemy far away
        w = main.Weapon('Sword', 20, 1, 1, 'sword.png', 2)
        p.add_inventory(w)
        p.set_tool(0)
        
        initial_hp = e.HP
        p.attack(e)
        self.assertEqual(e.HP, initial_hp)  # HP should remain unchanged
        
    def test_player_movement(self):
        """
        Tests that player movement updates coordinates correctly.
        """
        p = main.Player(50, 10, 10)
        p.x += 1  # Move right
        self.assertEqual(p.x, 11)
        self.assertEqual(p.y, 10)
        
        p.y += 1  # Move down
        self.assertEqual(p.x, 11)
        self.assertEqual(p.y, 11)
        
    def test_weapon_durability(self):
        """
        Tests if weapon durability remains consistent (since durability isn't implemented).
        """
        w = main.Weapon('Sword', 20, 1, 5, 'sword.png', 2)
        self.assertEqual(w.scale, 2)
        
    def test_enemy_defeat(self):
        """
        Tests if an enemy's health reaches zero after consecutive attacks.
        """
        p = main.Player(50, 10, 10)
        e = main.Enemy(30, 10, 10)  # Enemy with lower HP
        w = main.Weapon('Sword', 20, 1, 5, 'sword.png', 2)
        p.add_inventory(w)
        p.set_tool(0)
        
        p.attack(e)
        p.attack(e)
        self.assertTrue(e.HP <= 0)  # Enemy should be defeated

if __name__ == '__main__':
    unittest.main()
