import unittest
import main

class TestStringMethods(unittest.TestCase):

    ''' examples:
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())
    '''
    
    def test_movement(self):
        p = main.Player(10, 10, 10)
        unittest.assertEquals(p.x,10)

if __name__ == '__main__':
    unittest.main()