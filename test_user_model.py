"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from flask.globals import session
from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


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

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

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

    def test_follows(self):
        """Can you follow?"""

        u1 = User(email='test@test.com', username='test', password='password')

        u2 = User(email='test@test2.com',
                  username='test2', password='password2')

        db.session.add(u1, u2)
        db.session.commit()

        u1.following.append(u2)
        db.session.commit()

        self.assertEqual(len(u2.following), 0)
        self.assertEqual(len(u2.followers), 1)
        self.assertEqual(len(u1.followers), 0)
        self.assertEqual(len(u1.following), 1)

        self.assertEqual(u2.followers[0].id, u1.id)
        self.assertEqual(u1.following[0].id, u2.id)

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))

    def test_signup(self):
        """Register a user"""

        user = User.signup('testname', 'email@email.com',
                           'password', None)
        user.id = 999
        db.session.add(user)

        test = User.query.get(user.id)
        self.assertIsNotNone(test)
        self.assertEqual(user.username, 'testname')
        self.assertEqual(user.email, 'email@email.com')
        self.assertNotEqual(user.password, 'password')
        self.assertTrue(user.password.startswith('$2b$'))

    def test_invalid_signup(self):

        user = User.signup(None, 'test@email.com', 'password', None)
        user.id = 99999
        db.session.add(user)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authentication(self):

        user = User.signup('testuser', 'test@email.com', 'password', None)
        db.session.add(user)

        u = User.authenticate(user.username, 'password')

        self.assertIsNotNone(u)
        self.assertEqual(user.id, u.id)
