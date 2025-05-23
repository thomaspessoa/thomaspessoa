from tests.base import BaseTestCase
from app import db, User # Assuming User model is needed for direct checks if any

class AuthTests(BaseTestCase):

    def test_login_logout_admin(self):
        """Test admin login and logout."""
        # Login
        response = self.login('testadmin', 'adminpass')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)
        self.assertIn(b'Welcome, testadmin (Admin)!', response.data)

        # Logout
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login - Bus Tracker Pro', response.data) # Should be redirected to login page
        self.assertIn(b'You have been logged out.', response.data)

    def test_login_logout_driver(self):
        """Test driver login and logout."""
        # Login
        response = self.login('testdriver', 'driverpass')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Driver Dashboard', response.data)
        self.assertIn(b'Welcome, testdriver (Driver)!', response.data)

        # Logout
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login - Bus Tracker Pro', response.data)
        self.assertIn(b'You have been logged out.', response.data)

    def test_login_invalid_username(self):
        """Test login with an invalid username."""
        response = self.login('wronguser', 'adminpass')
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Invalid username or password.', response.data)
        self.assertIn(b'Login - Bus Tracker Pro', response.data)


    def test_login_invalid_password(self):
        """Test login with an invalid password."""
        response = self.login('testadmin', 'wrongpassword')
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Invalid username or password.', response.data)
        self.assertIn(b'Login - Bus Tracker Pro', response.data)

    def test_access_admin_dashboard_unauthenticated(self):
        """Test access to /admin by unauthenticated user."""
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login - Bus Tracker Pro', response.data) # Should redirect to login
        self.assertIn(b'Please log in to access this page.', response.data) # Flash message

    def test_access_driver_dashboard_unauthenticated(self):
        """Test access to /driver by unauthenticated user."""
        response = self.client.get('/driver', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login - Bus Tracker Pro', response.data) # Should redirect to login
        self.assertIn(b'Please log in to access this page.', response.data) # Flash message

    def test_access_admin_dashboard_as_admin(self):
        """Test access to /admin by authenticated admin."""
        self.login('testadmin', 'adminpass')
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)
        self.logout()

    def test_access_driver_dashboard_as_driver(self):
        """Test access to /driver by authenticated driver."""
        self.login('testdriver', 'driverpass')
        response = self.client.get('/driver')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Driver Dashboard', response.data)
        self.logout()

    def test_access_admin_dashboard_as_driver(self):
        """Test access to /admin by authenticated driver (should be denied)."""
        self.login('testdriver', 'driverpass')
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 403) # Check for 403 Forbidden
        self.assertIn(b'Forbidden', response.data) # Standard Werkzeug 403 page
        # Check for flash message if possible (might be tricky if abort(403) prevents flash rendering in test client)
        # For now, status code 403 is the primary check.
        # The flash message "Access denied: Admins only." is set before abort(403)
        # To check it, we would need to inspect the session or have a custom error handler.
        # Let's try to get the response without follow_redirects to check the flash before abort
        self.logout()
        self.login('testdriver', 'driverpass')
        response_no_redirect = self.client.get('/admin')
        self.assertEqual(response_no_redirect.status_code, 403)
        # Flask's abort(403) by default doesn't process further to render a template with flashes
        # So checking response.data for the flash message directly after abort(403) won't work.
        # The 403 status is the key indicator here.

    def test_access_driver_dashboard_as_admin(self):
        """Test access to /driver by authenticated admin (should be denied)."""
        self.login('testadmin', 'adminpass')
        response = self.client.get('/driver', follow_redirects=True)
        self.assertEqual(response.status_code, 403) # Check for 403 Forbidden
        self.assertIn(b'Forbidden', response.data)
        self.logout()

if __name__ == '__main__':
    unittest.main()
