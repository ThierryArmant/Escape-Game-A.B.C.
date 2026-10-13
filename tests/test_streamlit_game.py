import unittest
from abc_game import Store, cost

class GameTests(unittest.TestCase):
    def test_shared_game_and_flood(self):
        store = Store()
        master = store.create()
        manager, students, supplier = [store.join(master['code'], role) for role in ('manager', 'students', 'supplier')]
        store.action(manager, 'menu', value='regional')
        self.assertEqual(store.read(students)['first']['cost'], 1440)
        with self.assertRaises(ValueError): store.action(students, 'event', value='inondation')
        for auth in (students, supplier): store.action(auth, 'approve')
        store.action(master, 'next')
        store.action(students, 'service', value='explique')
        with self.assertRaises(ValueError): store.action(manager, 'measure', grams=100, percent=8)
        store.action(manager, 'measure', grams=40, percent=8)
        store.action(master, 'event', value='inondation')
        store.action(master, 'next')
        with self.assertRaises(ValueError): store.action(manager, 'menu', value='regional')
        store.action(manager, 'menu', value='secours')
        self.assertEqual(store.read(students)['second']['cost'], 1080)
        for auth in (students, supplier): store.action(auth, 'approve')
        store.action(master, 'next')
        self.assertEqual(store.read(master)['phase'], 4)
    def test_price_and_revalidation(self):
        self.assertEqual(cost('regional', 'secheresse'), 1485)
        store = Store(); master = store.create(); manager = store.join(master['code'], 'manager'); supplier = store.join(master['code'], 'supplier')
        store.action(manager, 'menu', value='vegetal'); store.action(supplier, 'approve'); store.action(manager, 'menu', value='regional')
        self.assertFalse(store.read(master)['approvals']['supplier'])
        with self.assertRaises(ValueError): store.join(master['code'], 'master')
        with self.assertRaises(ValueError): store.read(dict(master, token='faux'))

if __name__ == '__main__': unittest.main()
