import unittest
from abc_game import Store, cost, harvest, requirements

class GuidedStore(Store):
    """Simulate the teacher starting and resuming each common reading pause."""
    def create(self):
        auth = super().create()
        self.master = auth
        super().action(auth, 'start_game')
        return auth
    def action(self, auth, action, **values):
        super().action(auth, action, **values)
        if self.read(auth).get('reflection'):
            super().action(self.master, 'resume_reflection')

class ChoiceGameTests(unittest.TestCase):
    def setup_game(self, source='regional', mode='conventionnel'):
        store=GuidedStore();master=store.create();roles={r:store.join(master['code'],r) for r in ('manager','students','supplier')}
        store.action(roles['supplier'],'production',value=mode,source=source)
        return store,master,roles
    def play(self,source,mode):
        store,master,r=self.setup_game(source,mode)
        store.action(r['manager'],'plans',first=source,second='vegetal')
        self.assertEqual(requirements(store.read(master))['Carottes'],180)
        self.assertTrue(store.read(master)['harvest_done'])
        store.action(r['supplier'],'approve');store.action(r['students'],'approve')
        self.assertEqual(store.read(master)['phase'],1)
        store.action(master,'next')
        self.assertEqual(store.read(master)['phase'],2)
        store.action(r['students'],'service',value='unique',self_service='tout')
        self.assertTrue(store.read(master)['measure'])
        self.assertEqual(store.read(master)['phase'],2)
        store.action(r['manager'],'review_waste')
        store.action(master,'next')
        state=store.read(master);self.assertEqual(state['phase'],3);self.assertEqual(state['event'],'secheresse');self.assertEqual(state['day1']['waste'],60)
        self.assertIsNotNone(state['second'])
        with self.assertRaises(ValueError):store.action(r['manager'],'menu',value='vegetal')
        store.action(master,'climate_resume')
        store.action(r['manager'],'menu',value='vegetal',reuse=True,adaptation='Proposer de goûter')
        h=harvest(store.read(master));self.assertEqual(h['quantity'],45);self.assertEqual(h['need'],81)
        with self.assertRaises(ValueError):store.action(r['supplier'],'approve')
        store.action(r['supplier'],'strategy',value='complement')
        store.action(r['supplier'],'approve');store.action(r['students'],'approve')
        self.assertEqual(store.read(master)['phase'],3)
        store.action(master,'next')
        self.assertEqual(store.read(master)['phase'],4)
        self.assertIsNone(store.read(master)['service'])
        store.action(r['students'],'service',value='explique',self_service='faim')
        store.action(r['manager'],'review_waste')
        store.action(master,'next')
        state=store.read(master);self.assertEqual(state['phase'],5);self.assertEqual(state['day2']['waste'],18)
        self.assertLessEqual(state['first']['cost']+state['second']['cost'],3000)
    def test_all_offers_and_auto_reactions(self):
        for source in ['regional','importe']:
            for mode in ['bio','conventionnel']:
                with self.subTest(source=source,mode=mode):self.play(source,mode)
    def test_variety_permissions_and_preservation(self):
        store,master,r=self.setup_game()
        store.action(r['manager'],'plans',first='regional',second='regional')
        self.assertEqual(store.read(master)['second']['id'],'regional')
        with self.assertRaises(ValueError):store.action(r['students'],'climate_resume')
        store.action(r['manager'],'plans',first='vegetal',second='regional')
        self.assertEqual(store.read(master)['original_second']['id'],'regional')
        store.action(r['manager'],'plans',first='importe',second='vegetal')
        self.assertEqual(store.read(master)['first']['id'],'importe')
    def test_beef_budget_and_climate(self):
        store, master, r = self.setup_game()
        store.action(r['manager'], 'plans', first='boeuf', second='boeuf')
        state = store.read(master)
        self.assertEqual(state['first']['cost'] + state['second']['cost'], 3240)
        with self.assertRaises(ValueError): store.action(r['supplier'], 'approve')
        store.action(r['manager'], 'plans', first='boeuf', second='vegetal')
        self.assertEqual(store.read(master)['first']['cost'] + store.read(master)['second']['cost'], 2538)
        store.action(r['supplier'], 'approve')
        store.action(r['students'], 'approve')
        self.assertEqual(store.read(master)['phase'], 1)
        store.action(master, 'next')
        self.assertEqual(store.read(master)['phase'], 2)
    def test_cheaper_beef_offer(self):
        store=GuidedStore();master=store.create();broker=store.join(master['code'],'supplier');chef=store.join(master['code'],'manager')
        store.action(broker,'production',value='conventionnel',source='importe',animal_offer='boeuf_bresil')
        store.action(chef,'plans',first='boeuf_bresil',second='boeuf_bresil')
        self.assertEqual(store.read(master)['first']['cost'] + store.read(master)['second']['cost'],2520)
    def test_prices(self):
        self.assertEqual(cost('regional',mode='bio'),1500)
        self.assertEqual(cost('importe'),1242)
        self.assertEqual(cost('vegetal','secheresse',reuse=True),909)

if __name__=='__main__':unittest.main()

class CommonPauseTests(unittest.TestCase):
    def test_parallel_start_broadcast_pause_and_clock(self):
        from abc_game import elapsed
        store = Store(); master = store.create()
        roles = {r: store.join(master['code'], r) for r in ('students', 'manager', 'supplier')}
        self.assertEqual(elapsed(store.read(master), now=9999999999), 0)
        with self.assertRaises(ValueError):
            store.action(roles['manager'], 'plans', first='vegetal', second='regional')
        store.action(master, 'start_game')
        # Chef can send both menus before a broker offer exists.
        store.action(roles['manager'], 'plans', first='vegetal', second='regional')
        state = store.read(master)
        self.assertIsNone(state['production'])
        self.assertEqual(state['reflection']['role'], 'manager')
        frozen = elapsed(state, now=9999999999)
        self.assertEqual(frozen, elapsed(state, now=19999999999))
        for auth in roles.values():
            self.assertEqual(store.read(auth)['reflection'], state['reflection'])
        with self.assertRaises(ValueError):
            store.action(roles['supplier'], 'production', value='bio')
        with self.assertRaises(ValueError):
            store.action(roles['students'], 'resume_reflection')
        store.action(master, 'resume_reflection')
        # Pupils can express a request even when menus are already drafted.
        store.action(roles['students'], 'preferences', first='importe', second='vegetal')
        store.action(master, 'resume_reflection')
        store.action(roles['supplier'], 'production', value='bio', source='regional')
        state = store.read(master)
        self.assertEqual(state['first']['cost'], cost('vegetal', mode='bio'))
        self.assertFalse(state['approvals']['students'])

class AbcMenuTests(unittest.TestCase):
    def test_observed_rates_drive_scenario_and_recycling_choice(self):
        from abc_game import initial, apply, waste
        s=initial();apply(s,'master','start_game')
        apply(s,'manager','plans',first='abc_cantine',second='vegetal')
        self.assertEqual(requirements(s)['Chou-fleur en gratin'],90)
        apply(s,'master','resume_reflection')
        s['phase']=2
        apply(s,'students','service',value='unique',self_service='tout')
        self.assertEqual(waste(s),106)
        apply(s,'master','resume_reflection')
        apply(s,'supplier','valorisation',value='compostage')
        self.assertEqual(s['waste_policy']['2'],'compostage')
        self.assertEqual(s['reflection']['role'],'supplier')
