import unittest
from abc_game import Store, cost, harvest, requirements

class ChoiceGameTests(unittest.TestCase):
    def setup_game(self, source='regional', mode='conventionnel'):
        store=Store();master=store.create();roles={r:store.join(master['code'],r) for r in ('manager','students','supplier')}
        store.action(roles['supplier'],'production',value=mode,source=source)
        return store,master,roles
    def play(self,source,mode):
        store,master,r=self.setup_game(source,mode)
        store.action(r['manager'],'plans',first=source,second='vegetal')
        self.assertEqual(requirements(store.read(master))['Carottes'],180)
        self.assertTrue(store.read(master)['harvest_done'])
        store.action(r['supplier'],'approve');store.action(r['students'],'approve')
        self.assertEqual(store.read(master)['phase'],2)
        store.action(r['students'],'service',value='unique',self_service='tout')
        self.assertTrue(store.read(master)['measure'])
        self.assertEqual(store.read(master)['phase'],2)
        store.action(r['manager'],'review_waste')
        state=store.read(master);self.assertEqual(state['phase'],3);self.assertEqual(state['event'],'secheresse');self.assertEqual(state['day1']['waste'],60)
        self.assertIsNotNone(state['second'])
        with self.assertRaises(ValueError):store.action(r['manager'],'menu',value='vegetal')
        store.action(master,'climate_resume')
        store.action(r['manager'],'menu',value='vegetal',reuse=True,adaptation='Proposer de goûter')
        h=harvest(store.read(master));self.assertEqual(h['quantity'],45);self.assertEqual(h['need'],81)
        with self.assertRaises(ValueError):store.action(r['supplier'],'approve')
        store.action(r['supplier'],'strategy',value='complement')
        store.action(r['supplier'],'approve');store.action(r['students'],'approve')
        self.assertEqual(store.read(master)['phase'],4)
        self.assertIsNone(store.read(master)['service'])
        store.action(r['students'],'service',value='explique',self_service='faim')
        store.action(r['manager'],'review_waste')
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
        with self.assertRaises(ValueError):store.action(r['manager'],'plans',first='importe',second='vegetal')
        self.assertEqual(store.read(master)['first']['id'],'vegetal')
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
        self.assertEqual(store.read(master)['phase'], 2)
    def test_cheaper_beef_offer(self):
        store=Store();master=store.create();broker=store.join(master['code'],'supplier');chef=store.join(master['code'],'manager')
        store.action(broker,'production',value='conventionnel',source='importe',animal_offer='boeuf_bresil')
        store.action(chef,'plans',first='boeuf_bresil',second='boeuf_bresil')
        self.assertEqual(store.read(master)['first']['cost'] + store.read(master)['second']['cost'],2520)
    def test_prices(self):
        self.assertEqual(cost('regional',mode='bio'),1500)
        self.assertEqual(cost('importe'),1242)
        self.assertEqual(cost('vegetal','secheresse',reuse=True),909)

if __name__=='__main__':unittest.main()
