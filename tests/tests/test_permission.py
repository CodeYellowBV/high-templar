from high_templar.authentication import Permission

from unittest import TestCase


class TestPermissionOrdering(TestCase):
    def test_permission_more(self):
        p1 = Permission({
            "target": 'reassignment-change-finished',
            "allocation": '*',
            "driver": '*',
            "truck": '*',
        })

        p2 = Permission({
            "target": 'reassignment-change-finished',
            "allocation": 1,
            "driver": '*',
            "truck": '*',
        })


        self.assertTrue(p2 < p1)
        self.assertTrue(p2 <= p1)
        self.assertFalse(p2 > p1)
        self.assertFalse(p2 >= p1)
        self.assertFalse(p2 == p1)

        self.assertFalse(p1 < p2)
        self.assertFalse(p1 <= p2)

        self.assertTrue(p1 >= p2)
        self.assertFalse(p1 == p2)

        self.assertFalse(p1 > p1)
        self.assertFalse(p1 < p1)