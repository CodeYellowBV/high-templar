from unittest import TestCase

from high_templar.authentication import Permission


class TestPermission(TestCase):
    def test_permission_equal(self):
        p1 = Permission({
            "target": "message",
            "customer": "1"
        })

        p2 = Permission({
            "target": "message",
            "customer": "1"
        })

        self.assertEqual(p1, p2)

    def test_permission_ordering(self):
        p1 = Permission({
            "target": "message",
            "customer": "1"
        })

        p2 = Permission({
            "target": "message",
            "customer": "*"
        })

        # p2 has strictly more permissions that p1, so it hold that p1 > p2

        self.assertFalse(p1 == p2)

        self.assertTrue(p2 > p1)
        self.assertTrue(p2 >= p1)
        self.assertTrue(p1 < p2)
        self.assertTrue(p1 <= p2)
        self.assertFalse(p1 > p2)
        self.assertFalse(p1 >= p2)
        self.assertFalse(p2 < p1)
        self.assertFalse(p2 <= p1)

    def test_permission_not_orderable_different_keys(self):
        p1 = Permission({
            "target": "message",
            "customer": "1"
        })

        p2 = Permission({
            "target": "message",
            "bar": "*"
        })

        self.assertFalse(p2 == p1)
        self.assertFalse(p2 > p1)
        self.assertFalse(p2 >= p1)
        self.assertFalse(p1 < p2)
        self.assertFalse(p1 <= p2)
        self.assertFalse(p1 > p2)
        self.assertFalse(p1 >= p2)
        self.assertFalse(p2 < p1)
        self.assertFalse(p2 <= p1)

    def test_permission_not_orderable_same_keys(self):
        p1 = Permission({
            "target": "message",
            "customer": "1"
        })

        p2 = Permission({
            "target": "message",
            "customer": "2"
        })

        self.assertFalse(p2 == p1)
        self.assertFalse(p2 > p1)
        self.assertFalse(p2 >= p1)
        self.assertFalse(p1 < p2)
        self.assertFalse(p1 <= p2)
        self.assertFalse(p1 > p2)
        self.assertFalse(p1 >= p2)
        self.assertFalse(p2 < p1)
        self.assertFalse(p2 <= p1)
