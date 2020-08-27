"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(f"{u}", f"<User #{u.id}: {u.username}, {u.email}>")
    
    def test_is_following(self):
        """test if following"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add_all([u, u2])
        db.session.commit()
        
        u.following.append(u2)
        self.assertEqual(u.is_following(u2), 1)
        self.assertEqual(u2.is_followed_by(u), 1)

    def test_is_following_false(self):
        """test if following returns false if not following"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add_all([u, u2])
        db.session.commit()
        

        self.assertEqual(u.is_following(u2), 0)
        self.assertEqual(u2.is_followed_by(u), 0)

    def test_user_create(self):
        """test creating a new user"""
        u=User.signup("testname", "testemail@email.com", "password", "image_url")
        db.session.commit()
        

        self.assertEqual(f"{u}", f"<User #{u.id}: {u.username}, {u.email}>")

    def test_user_create_error(self):        
        """test that invalid cridentials return errors"""
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)

    def test_user_authenticate(self):
        """test user authentication"""
        u=User.signup("testname", "testemail@email.com", "password", "image_url")

        u=User.authenticate("testname", "password")
        
        self.assertEqual(f"{u}", f"<User #{u.id}: {u.username}, {u.email}>")
    
    def test_user_authenticate_error(self):
        """test that invalid password return errors"""
        u=User.signup("testname", "testemail@email.com", "password", "image_url")

        u=User.authenticate("testname", "password2")
        
        self.assertEqual(u, False)
    
    def test_user_authenticate_username_error(self):
        """test that invalid username return errors"""
        u=User.signup("testname", "testemail@email.com", "password", "image_url")

        u=User.authenticate("testname2", "password")
        
        self.assertEqual(u, False)