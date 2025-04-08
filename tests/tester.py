import requests
import unittest
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:3000'

class TestMeetingRoomAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Connexion en tant qu'admin
        admin_credentials = {"username": "admin", "password": "admin"}
        r = requests.post(f"{BASE_URL}/auth/login", json=admin_credentials)
        assert r.status_code == 200, "Echec de la connexion admin"
        cls.admin_token = r.json()['token']

        # Connexion en tant qu'employé
        employee_credentials = {"username": "employee", "password": "employee"}
        r = requests.post(f"{BASE_URL}/auth/login", json=employee_credentials)
        assert r.status_code == 200, "Echec de la connexion employee"
        cls.employee_token = r.json()['token']
        
        # Créer une salle à utiliser dans tous les tests
        headers = {'Authorization': f'Bearer {cls.admin_token}'}
        room_data = {
            "name": "Salle Test",
            "capacity": 10,
            "features": ["TV", "Tableau blanc"],
            "rules": {
                "maxDurationMinutes": 120,
                "allowWeekends": False,
                "minAdvanceHours": 3
            }
        }
        r = requests.post(f"{BASE_URL}/rooms", json=room_data, headers=headers)
        if r.status_code == 201:
            created_room = r.json()
            cls.created_room_id = created_room["id"]
        else:
            raise Exception("La création de la salle a échoué dans setUpClass.")

    def test_get_rooms(self):
        """Teste la récupération de la liste des salles via GET /rooms"""
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        r = requests.get(f"{BASE_URL}/rooms", headers=headers)
        self.assertEqual(r.status_code, 200)
        rooms = r.json()
        self.assertIsInstance(rooms, list)

    def test_create_room_admin(self):
        """Teste la création d'une salle en tant qu'admin via POST /rooms"""
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        room_data = {
            "name": "Salle Test",
            "capacity": 10,
            "features": ["TV", "Tableau blanc"],
            "rules": {
                "maxDurationMinutes": 120,
                "allowWeekends": False,
                "minAdvanceHours": 3
            }
        }
        r = requests.post(f"{BASE_URL}/rooms", json=room_data, headers=headers)
        print("Response status code for room creation:", r.status_code)
        print("Response content:", r.text)
        self.assertEqual(r.status_code, 201, msg=r.json())
        created_room = r.json()
        self.assertIn("id", created_room)
        self.__class__.created_room_id = created_room["id"]

    def test_get_room_details(self):
        """Teste la consultation du détail d'une salle via GET /rooms/:id"""
        room_id = getattr(self.__class__, 'created_room_id', None)
        self.assertIsNotNone(room_id, "La salle n'a pas été créée dans test_create_room_admin")
        r = requests.get(f"{BASE_URL}/rooms/{room_id}")
        self.assertEqual(r.status_code, 200)
        room_detail = r.json()
        self.assertEqual(room_detail["id"], room_id)

    def test_create_booking(self):
        """Teste la création d'une réservation valide via POST /bookings"""
        room_id = getattr(self.__class__, 'created_room_id', None)
        self.assertIsNotNone(room_id, "La salle n'a pas été créée dans setUpClass")
        headers = {'Authorization': f'Bearer {self.employee_token}'}
        
        # Utiliser la date de demain pour ce test
        booking_date = datetime.now() + timedelta(days=1)
        start = booking_date.replace(hour=10, minute=0, second=0, microsecond=0)
        end = booking_date.replace(hour=11, minute=0, second=0, microsecond=0)
        booking_data = {
            "roomId": room_id,
            "start": start.isoformat(),
            "end": end.isoformat()
        }
        r = requests.post(f"{BASE_URL}/bookings", json=booking_data, headers=headers)
        self.assertEqual(r.status_code, 201, msg=r.json())
        booking = r.json()
        self.assertIn("id", booking)
        self.__class__.created_booking_id = booking["id"]

    def test_conflicting_booking(self):
        """Teste la détection d'un conflit de réservation via POST /bookings"""
        room_id = getattr(self.__class__, 'created_room_id', None)
        self.assertIsNotNone(room_id, "La salle n'a pas été créée dans setUpClass")
        headers = {'Authorization': f'Bearer {self.employee_token}'}
        
        # Utiliser une autre date (par exemple, le jour d'après demain) pour isoler ce test
        booking_date = datetime.now() + timedelta(days=2)
        # Créer d'abord une réservation valide de 10h à 11h
        start1 = booking_date.replace(hour=10, minute=0, second=0, microsecond=0)
        end1 = booking_date.replace(hour=11, minute=0, second=0, microsecond=0)
        booking_data1 = {
            "roomId": room_id,
            "start": start1.isoformat(),
            "end": end1.isoformat()
        }
        r1 = requests.post(f"{BASE_URL}/bookings", json=booking_data1, headers=headers)
        self.assertEqual(r1.status_code, 201, msg=r1.json())

        # Tenter ensuite de créer une réservation qui chevauche : de 10h30 à 11h30
        start2 = booking_date.replace(hour=10, minute=30, second=0, microsecond=0)
        end2 = booking_date.replace(hour=11, minute=30, second=0, microsecond=0)
        booking_data2 = {
            "roomId": room_id,
            "start": start2.isoformat(),
            "end": end2.isoformat()
        }
        r2 = requests.post(f"{BASE_URL}/bookings", json=booking_data2, headers=headers)
        # La requête doit renvoyer une erreur (statut 400)
        self.assertEqual(r2.status_code, 400, msg=f"Réponse reçue : {r2.json()}")
        error_msg = r2.json().get("error")
        self.assertIsNotNone(error_msg)

    def test_get_bookings_employee(self):
        """Teste la récupération des réservations pour un employé via GET /bookings"""
        headers = {'Authorization': f'Bearer {self.employee_token}'}
        r = requests.get(f"{BASE_URL}/bookings", headers=headers)
        self.assertEqual(r.status_code, 200)
        bookings = r.json()
        self.assertIsInstance(bookings, list)

    def test_get_bookings_admin(self):
        """Teste la récupération de toutes les réservations en tant qu'admin via GET /bookings"""
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        r = requests.get(f"{BASE_URL}/bookings", headers=headers)
        self.assertEqual(r.status_code, 200)
        bookings = r.json()
        self.assertIsInstance(bookings, list)

    def test_room_availability(self):
        """Teste la route d'affichage des créneaux disponibles via GET /rooms/:id/availability?date=YYYY-MM-DD"""
        room_id = getattr(self.__class__, 'created_room_id', None)
        self.assertIsNotNone(room_id, "La salle n'a pas été créée dans setUpClass")
        # Par exemple, utiliser la date de demain pour tester la disponibilité
        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        r = requests.get(f"{BASE_URL}/rooms/{room_id}/availability?date={tomorrow_date}")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # Modifier le test pour vérifier la présence de la clé 'availability'
        self.assertIn("availability", data)

if __name__ == '__main__':
    unittest.main()