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

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        Message.query.delete()
        User.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work and link user to message?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        
        m = Message(
            text="message text"
        )
        u.messages.append(m)
        db.session.add(m)
        db.session.commit()


        self.assertEqual(len(u.messages), 1)
        self.assertEqual(m.user_id, u.id)
        
    def test_message_likes(self):  
        """test messages that a user likes"""      
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        
        m = Message(
            text="message text"
        )
        u.messages.append(m)
        u.likes.append(m)
        db.session.add(m)
        db.session.commit()

        self.assertEqual(u.likes, [m])

    