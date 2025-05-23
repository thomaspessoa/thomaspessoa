from tests.base import BaseTestCase
from app import db, Trip, User # Import necessary models
from datetime import datetime, timedelta

class TripManagementTests(BaseTestCase):

    def test_driver_start_trip_success(self):
        """Test driver successfully starting a new trip."""
        self.login('testdriver', 'driverpass')
        destino_val = "Centro da Cidade"
        horario_val = "10:00 AM"
        expected_schedule_str = f"Destino: {destino_val} - Horário: {horario_val}"
        
        response = self.client.post('/start_trip', data={'destino': destino_val, 'horario_viagem': horario_val}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Viagem iniciada com sucesso!', response.data) # Translated
        
        with self.app.app_context(): 
            driver_user = User.query.filter_by(username='testdriver').first()
            trip = Trip.query.filter_by(driver_id=driver_user.id, status='active').first()
            self.assertIsNotNone(trip)
            self.assertEqual(trip.schedule, expected_schedule_str)
            self.assertIsNotNone(trip.start_time)
            self.assertIsNone(trip.end_time)
        self.logout()

    def test_driver_start_trip_no_schedule(self): # Renamed to reflect new fields
        """Test driver attempting to start a trip without providing Destino or Horario."""
        self.login('testdriver', 'driverpass')
        
        # Test with empty destino
        response_no_destino = self.client.post('/start_trip', data={'destino': '', 'horario_viagem': '10:00 AM'}, follow_redirects=True)
        self.assertEqual(response_no_destino.status_code, 200)
        self.assertIn(b'Destino e Hor\xc3\xa1rio da Viagem s\xc3\xa3o obrigat\xc3\xb3rios.', response_no_destino.data) # Translated & UTF-8 encoded
        self.assertIn(b'Painel do Motorista', response_no_destino.data) 

        # Test with empty horario_viagem
        response_no_horario = self.client.post('/start_trip', data={'destino': 'Centro', 'horario_viagem': ''}, follow_redirects=True)
        self.assertEqual(response_no_horario.status_code, 200)
        self.assertIn(b'Destino e Hor\xc3\xa1rio da Viagem s\xc3\xa3o obrigat\xc3\xb3rios.', response_no_horario.data) # Translated & UTF-8 encoded
        self.assertIn(b'Painel do Motorista', response_no_horario.data)
        
        with self.app.app_context(): 
            driver_user = User.query.filter_by(username='testdriver').first()
            trip = Trip.query.filter_by(driver_id=driver_user.id, status='active').first()
            self.assertIsNone(trip) # No trip should have been created
        self.logout()

    def test_driver_start_trip_already_active(self):
        """Test driver attempting to start a new trip when one is already active."""
        self.login('testdriver', 'driverpass')
        # Start one trip
        self.client.post('/start_trip', data={'destino': 'Primeira Viagem Dest', 'horario_viagem': '11:00'}, follow_redirects=True)
        
        # Attempt to start another
        response = self.client.post('/start_trip', data={'destino': 'Segunda Viagem Dest', 'horario_viagem': '12:00'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Voc\xc3\xaa j\xc3\xa1 possui uma viagem ativa.', response.data) # Translated
        
        with self.app.app_context(): 
            driver_user = User.query.filter_by(username='testdriver').first()
            active_trips = Trip.query.filter_by(driver_id=driver_user.id, status='active').count()
            self.assertEqual(active_trips, 1) # Only one active trip should exist
            
            expected_first_schedule = "Destino: Primeira Viagem Dest - Horário: 11:00"
            first_trip = Trip.query.filter_by(driver_id=driver_user.id, schedule=expected_first_schedule).first()
            self.assertIsNotNone(first_trip)
            self.assertEqual(first_trip.status, 'active')
        self.logout()

    def test_driver_end_trip_success(self):
        """Test driver successfully ending an active trip."""
        self.login('testdriver', 'driverpass')
        self.client.post('/start_trip', data={'destino': 'Viagem para Finalizar', 'horario_viagem': '15:00'}, follow_redirects=True)
        
        with self.app.app_context(): 
            driver_user = User.query.filter_by(username='testdriver').first()
            trip_to_end = Trip.query.filter_by(driver_id=driver_user.id, status='active').first()
            self.assertIsNotNone(trip_to_end)

        response = self.client.post('/end_trip', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Viagem finalizada com sucesso.', response.data) # Translated
        
        with self.app.app_context(): 
            ended_trip = db.session.get(Trip, trip_to_end.id) 
            self.assertEqual(ended_trip.status, 'completed')
            self.assertIsNotNone(ended_trip.end_time)
        self.logout()

    def test_driver_end_trip_none_active(self):
        """Test driver attempting to end a trip when none is active."""
        self.login('testdriver', 'driverpass')
        response = self.client.post('/end_trip', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Nenhuma viagem ativa encontrada para finalizar.', response.data) # Translated
        self.logout()

    def test_admin_view_dashboard_no_active_trips(self):
        """Test admin dashboard when no trips are active."""
        self.login('testadmin', 'adminpass') # testadmin uses 'adminpass' as per BaseTestCase
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Nenhum \xc3\xb4nibus em rota atualmente.', response.data) # Translated "No buses currently on route."
        self.logout()

    def test_admin_view_dashboard_with_active_trip(self):
        """Test admin dashboard when a trip is active."""
        # Driver starts a trip
        self.login('testdriver', 'driverpass')
        destino_val = "Viagem ao Vivo para Admin"
        horario_val = "Agora"
        expected_schedule_str = f"Destino: {destino_val} - Horário: {horario_val}"
        self.client.post('/start_trip', data={'destino': destino_val, 'horario_viagem': horario_val}, follow_redirects=True)
        self.logout()

        # Admin logs in and views dashboard
        self.login('testadmin', 'adminpass') # testadmin uses 'adminpass'
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Nenhum \xc3\xb4nibus em rota atualmente.', response.data) # Translated
        self.assertIn(b'testdriver', response.data) # Driver's username
        self.assertIn(expected_schedule_str.encode('utf-8'), response.data) # Schedule
        self.assertIn(b'active', response.data) # Status (assuming status itself is not translated in display)
        self.logout()

if __name__ == '__main__':
    unittest.main()
