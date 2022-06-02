from django.test import TestCase
from .models import CW_players

class CW_PlayersTestCase(TestCase):
    def setUp(self) -> None:
        CW_players.objects.create(chw_username="Test", session="test_session")

    def test_create_player(self):
        test_player = CW_players.objects.get(chw_username="Test")
        self.assertEqual(test_player.chw_username, "Test")

    