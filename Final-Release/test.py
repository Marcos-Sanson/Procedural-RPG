import unittest
import main

class TestGame(unittest.TestCase):

    ''' examples:
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())
    '''
    
    def test_init_player(self):
        p = main.Player(50, 10, 10)
        self.assertEqual(p.x, 10)
        self.assertEqual(p.y, 10)
        self.assertEqual(None, p.get_tool())

    def test_init_enemy(self):
        e = main.Enemy(50, 10, 10)
        self.assertEqual(e.x, 10)
        self.assertEqual(e.y, 10)
        self.assertEqual(e.HP, 50)
        
    def test_new_weapon(self):
        p = main.Player(50, 10, 10)
        w = main.Weapon('Sword', 20, 1, 5, None, 2)
        self.assertEqual(w.reach, 5)
        
    def test_attack_enemy(self):
        p = main.Player(50, 10, 10)
        e = main.Enemy(50, 10, 10)
        
        # this attack should be within range, and do damage to the enemy
        p.attack(e)
        self.assertTrue(e.HP < 50)
        

if __name__ == '__main__':
    unittest.main()