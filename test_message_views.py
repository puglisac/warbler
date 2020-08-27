"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY, do_logout

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()
        


    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_loggedout(self):
        """logged out user should not be able to add message?"""


        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_message_unauth(self):
        """unauth user should not be able to add message as another user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 0
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))


    def test_message_detail(self):
        """can user see message details?"""
            # test message detail page
            
        m=Message(id=0, text="message text", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg=Message.query.get(0)
            resp = c.get(f"/messages/0")
            
            html = resp.get_data(as_text=True)
            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn(msg.text, html)


    def test_message_delete(self):
        """can user delete message?"""
            
        m=Message(id=0, text="message text", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg=Message.query.get(0)
            resp = c.post(f"/messages/0/delete")
            
            html = resp.get_data(as_text=True)
            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertNotIn(msg.text, html)

    def test_message_delete_loggedout(self):
        """can user not delete message if logged out?"""
        
        m=Message(id=0, text="message text", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:  
            resp = c.post("/messages/0/delete", follow_redirects=True)
            

            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
    
    def test_message_delete_unauth(self):
        """can user not delete message if not authorized user?"""
        u=User()
        m=Message(id=0, text="message text", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:  
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 0
            
            resp = c.post("/messages/0/delete", follow_redirects=True)
            # Make sure it returns ok
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    
