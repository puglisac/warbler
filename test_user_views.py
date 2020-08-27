"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


from app import app, CURR_USER_KEY, do_logout
import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()

    def test_add_user(self):
        """can an unregistered user create a profile"""
        with self.client as c:
            resp = c.post("/signup", data={"username": "username", "password": "password",
                                           "email": "email@email.com"}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="small">Following</p>', html)

    def test_add_user_username_error(self):
        """can an unregistered user create a profile"""
        with self.client as c:
            resp = c.post("/signup", data={"username": "testuser",
                                           "password": "password", "email": "email@email.com"})
            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username already taken", str(resp.data))

    def test_login(self):
        """can a registered user login"""
        with self.client as c:
            resp = c.post(
                "/login", data={"username": "testuser", "password": "testuser"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)

    def test_user_home(self):
        """test user home page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p class="small">Following</p>', html)

    def test_user_following(self):
        """test view of following page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text=True)

            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="col-sm-9">', html)

    def test_user_following_unauth(self):
        """can an unauthorized user see user following"""
        with self.client as c:
            resp = c.get(
                f"/users/{self.testuser.id}/following", follow_redirects=True)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertIn("unauthorized", str(resp.data))

    def test_user_followers(self):
        """test view of followers page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)

            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="col-sm-9">', html)

    def test_user_following_unauth(self):
        """can an unauthorized user see user following"""
        with self.client as c:
            resp = c.get(
                f"/users/{self.testuser.id}/followers", follow_redirects=True)

            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn("unauthorized", str(resp.data))

    def test_add_following(self):
        """can a user follow another user"""
        follow_user = User(id=0, username="followed",
                           password="password", email="email@email.com")
        db.session.add(follow_user)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f"/users/follow/0", follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn("followed", html)

    def test_update_profile(self):
        """can a user update profile"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f"/users/{self.testuser.id}/profile", data={
                          "username": "newname", "password": "testuser"}, follow_redirects=True)

            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Updated", str(resp.data))

    def test_update_profile_wrong_pw(self):
        """can a user update profile"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f"/users/{self.testuser.id}/profile", data={
                          "username": "newname", "password": "testuser2"}, follow_redirects=True)

            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid Password", str(resp.data))
