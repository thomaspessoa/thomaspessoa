from tests.base import BaseTestCase
from app import db, Trip, User # Import necessary models
from datetime import datetime, timedelta

class TripManagementTests(BaseTestCase):

    def test_driver_start_trip_success(self):
        """Test driver successfully starting a new trip."""
        self.login('testdriver', 'driverpass')
        response = self.client.post('/start_trip', data={'schedule': 'Route A to B'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Trip started successfully!', response.data)
        
        with self.app.app_context(): # Use self.app here
            driver_user = User.query.filter_by(username='testdriver').first()
            trip = Trip.query.filter_by(driver_id=driver_user.id, status='active').first()
            self.assertIsNotNone(trip)
            self.assertEqual(trip.schedule, 'Route A to B')
            self.assertIsNotNone(trip.start_time)
            self.assertIsNone(trip.end_time)
        self.logout()

    def test_driver_start_trip_no_schedule(self):
        """Test driver attempting to start a trip without providing schedule info."""
        self.login('testdriver', 'driverpass')
        response = self.client.post('/start_trip', data={'schedule': ''}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Schedule information is required to start a trip.', response.data)
        self.assertIn(b'Driver Dashboard', response.data) # Should stay on driver dashboard
        
        with self.app.app_context(): # Use self.app here
            driver_user = User.query.filter_by(username='testdriver').first()
            trip = Trip.query.filter_by(driver_id=driver_user.id, status='active').first()
            self.assertIsNone(trip) # No trip should have been created
        self.logout()

    def test_driver_start_trip_already_active(self):
        """Test driver attempting to start a new trip when one is already active."""
        self.login('testdriver', 'driverpass')
        # Start one trip
        self.client.post('/start_trip', data={'schedule': 'First Trip'}, follow_redirects=True)
        
        # Attempt to start another
        response = self.client.post('/start_trip', data={'schedule': 'Second Trip'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You already have an active trip.', response.data)
        
        with self.app.app_context(): # Use self.app here
            driver_user = User.query.filter_by(username='testdriver').first()
            active_trips = Trip.query.filter_by(driver_id=driver_user.id, status='active').count()
            self.assertEqual(active_trips, 1) # Only one active trip should exist
            first_trip = Trip.query.filter_by(driver_id=driver_user.id, schedule='First Trip').first()
            self.assertIsNotNone(first_trip)
            self.assertEqual(first_trip.status, 'active')
        self.logout()

    def test_driver_end_trip_success(self):
        """Test driver successfully ending an active trip."""
        self.login('testdriver', 'driverpass')
        self.client.post('/start_trip', data={'schedule': 'Trip to End'}, follow_redirects=True)
        
        with self.app.app_context(): # Use self.app here
            driver_user = User.query.filter_by(username='testdriver').first()
            trip_to_end = Trip.query.filter_by(driver_id=driver_user.id, status='active').first()
            self.assertIsNotNone(trip_to_end)

        response = self.client.post('/end_trip', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Trip ended successfully.', response.data)
        
        with self.app.app_context(): # Use self.app here
            ended_trip = db.session.get(Trip, trip_to_end.id) # Use db.session.get
            self.assertEqual(ended_trip.status, 'completed')
            self.assertIsNotNone(ended_trip.end_time)
        self.logout()

    def test_driver_end_trip_none_active(self):
        """Test driver attempting to end a trip when none is active."""
        self.login('testdriver', 'driverpass')
        response = self.client.post('/end_trip', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No active trip found to end.', response.data)
        self.logout()

    def test_admin_view_dashboard_no_active_trips(self):
        """Test admin dashboard when no trips are active."""
        self.login('testadmin', 'adminpass')
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No buses currently on route.', response.data)
        self.logout()

    def test_admin_view_dashboard_with_active_trip(self):
        """Test admin dashboard when a trip is active."""
        # Driver starts a trip
        self.login('testdriver', 'driverpass')
        self.client.post('/start_trip', data={'schedule': 'Live Trip for Admin'}, follow_redirects=True)
        self.logout()

        # Admin logs in and views dashboard
        self.login('testadmin', 'adminpass')
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'No buses currently on route.', response.data)
        self.assertIn(b'testdriver', response.data) # Driver's username
        self.assertIn(b'Live Trip for Admin', response.data) # Schedule
        self.assertIn(b'active', response.data) # Status
        self.logout()

if __name__ == '__main__':
    unittest.main()
