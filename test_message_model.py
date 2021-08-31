
from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

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


class MessageModelTestCase(TestCase):
    """Message model"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        self.id = 988
        u = User.signup('testname', 'test@test.com', 'password', None)
        u.id = self.id
        db.session.commit()

        self.u = User.query.get(self.id)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):

        m = Message(text='Test Message', user_id=self.id)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, 'Test Message')

    def test_message_likes(self):

        m = Message(
            text='Message Test',
            user_id=self.id
        )

        db.session.add(m)
        db.session.commit()

        self.u.likes.append(m)

        l = Likes.query.filter(Likes.user_id == self.id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m.id)
