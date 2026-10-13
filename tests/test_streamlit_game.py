import unittest
from abc_game import Store, cost, harvest, waste

class GameTests(unittest.TestCase):
    def setup_game(self,mode='conventionnel'):
        store=Store();master=store.create()
        roles={r:store.join(master['code'],r) for r in ('manager','students','supplier')}
        store.action(roles['supplier'],'production',value=mode)
        return store,master,roles
    def confirm(self,store,roles):
        h=harvest(store.read(roles['supplier']))
        store.action(roles['supplier'],'harvest',answer=h['quantity'])
        enough=h['quantity']>=h['need']
        store.action(roles['supplier'],'supply',value='oui' if enough else 'non')
        if not enough:store.action(roles['supplier'],'strategy',value='complement')
        for r in ('supplier','students'):store.action(roles[r],'approve')
    def play(self,mode,event=None,reuse=False):
        store,master,roles=self.setup_game(mode)
        store.action(roles['manager'],'menu',value='regional')
        self.confirm(store,roles);store.action(master,'next')
        store.action(roles['students'],'service',value='explique',self_service='faim')
        w=waste(store.read(master));self.assertEqual(w,18)
        with self.assertRaises(ValueError):store.action(roles['manager'],'percent',answer=6)
        store.action(roles['manager'],'grams',answer=30)
        store.action(roles['manager'],'percent',answer=6)
        if event:store.action(master,'event',value=event)
        store.action(master,'next')
        menu='secours' if event=='inondation' else 'vegetal' if mode=='bio' and event=='secheresse' else 'regional'
        store.action(roles['manager'],'menu',value=menu,reuse=reuse,adaptation='Proposer de goûter')
        self.confirm(store,roles);store.action(master,'next')
        self.assertEqual(store.read(master)['phase'],4)
        return store.read(master)
    def test_full_games(self):
        for mode in ['bio','conventionnel']:
            for event in [None,'secheresse','inondation']:
                with self.subTest(mode=mode,event=event):self.play(mode,event,True)
    def test_bio_and_stock_prices(self):
        self.assertEqual(cost('regional',mode='bio'),1500)
        self.assertEqual(cost('regional',reuse=True),1425.6)
        self.assertEqual(cost('secours','inondation',reuse=True),1080)
        s=self.play('conventionnel',None,True)
        self.assertEqual(s['second']['cost'],1425.6)
    def test_roles_and_crop_checks(self):
        store,master,r=self.setup_game()
        with self.assertRaises(ValueError):store.action(r['students'],'event',value='inondation')
        store.action(r['manager'],'menu',value='regional')
        with self.assertRaises(ValueError):store.action(r['supplier'],'approve')
        with self.assertRaises(ValueError):store.action(r['supplier'],'harvest',answer=90)
        self.assertFalse(store.read(master)['harvest_done'])
        self.confirm(store,r)
        store.action(r['manager'],'menu',value='vegetal')
        self.assertFalse(store.read(master)['harvest_done'])
        self.assertFalse(store.read(master)['approvals']['supplier'])
    def test_service_invalidation_and_event_timing(self):
        store,master,r=self.setup_game();store.action(r['manager'],'menu',value='regional')
        self.confirm(store,r);store.action(master,'next')
        store.action(r['students'],'service',value='explique',self_service='tout')
        store.action(r['manager'],'grams',answer=40)
        store.action(r['students'],'service',value='unique',self_service='tout')
        self.assertFalse(store.read(master)['grams_done'])
        store.action(master,'event',value='inondation')
        self.assertEqual(store.read(master)['first']['cost'],1440)
        with self.assertRaises(ValueError):store.action(master,'event',value='secheresse')

if __name__=='__main__':unittest.main()
