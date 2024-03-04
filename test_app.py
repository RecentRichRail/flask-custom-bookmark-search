import unittest
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_redirect_commands(self):
        response = self.app.get('/search=cmds')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://search.spicerhome.net/')

    def test_redirect_command_g_search_query(self):
        response = self.app.get('/search=g search query')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://search.brave.com/search?q=search+query&source=web')

    def test_redirect_command_guest(self):
        response = self.app.get('/search=guest')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://wiki.spicerhome.net/index.php/Guest_WiFi')
    
    def test_redirect_test_search(self):
        response = self.app.get('/search=google search')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://search.brave.com/search?q=google+search&source=web')

if __name__ == '__main__':
    unittest.main()