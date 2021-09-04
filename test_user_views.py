
from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import Follows, db, connect_db, Message, User, Likes

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.u = User.signup(
            username='Tink',
            email='tink@bell.com',
            password='password',
            image_url=None
        )

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_show(self):

        with self.client as c:

            resp = c.get(f"/users/{self.u.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@Tink", str(resp.data))

    def test_add_like(self):

        u2 = User.signup(
            username='Test2',
            email='test2@email2.com',
            password='password',
            image_url=None
        )
        m = Message(id=1984, text="The earth is round", user_id=self.u.id)

        db.session.add_all([u2, m])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = u2.id

            resp = c.post("/users/add_like/1984",
                          follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == 1984).all()

            self.assertEqual(len(likes), 1)

    def test_add_follow(self):

        u3 = User.signup(
            username='Test3',
            email='test2@email2.com',
            password='password',
            image_url=None
        )
        db.session.add(u3)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = u3.id

            resp = c.post(f'/users/follow/{self.u.id}', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@Test3', str(resp.data))
