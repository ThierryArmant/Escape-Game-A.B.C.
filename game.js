export const menus = {regional:{name:'Poulet régional, pommes de terre, carottes',cost:1440},importe:{name:'Poulet importé, riz, carottes',cost:1242},vegetal:{name:'Lentilles, riz, carottes',cost:918},secours:{name:'Lentilles, riz de réserve, légumes surgelés',cost:900}};
export const services = {unique:{name:'Portion unique',waste:60},adapte:{name:'Petite portion et complément',waste:36},explique:{name:'Portion adaptée et recette présentée',waste:24}};
export function cost(menu,event){if(!menus[menu])throw Error('Menu inconnu');if(event==='inondation'&&menu!=='secours')throw Error('Récoltes détruites : choisissez le menu avec légumes de réserve');return menus[menu].cost+(event==='inondation'?180:0)+(event==='secheresse'&&menu!=='secours'?9+(menu==='regional'?36:0):0)}
export function initial(){return {phase:1,event:null,startedAt:Date.now(),hint:false,first:null,second:null,service:null,measure:false,approvals:{supplier:false,students:false},feedback:''}}
export function apply(s,role,a){
 if(role==='master'){
  if(a.type==='event'){if(!['secheresse','inondation'].includes(a.value)||s.event||s.phase===4)throw Error('Un seul aléa par partie');s.event=a.value;s.second=null;s.approvals={supplier:false,students:false};}
  else if(a.type==='hint')s.hint=true;
  else if(a.type==='next'){if(s.phase===1&&(!s.first||!s.approvals.supplier||!s.approvals.students))throw Error('Les trois équipes doivent valider la commande');if(s.phase===2&&!s.measure)throw Error('La mesure A.B.C. doit être résolue');if(s.phase===3&&(!s.second||!s.approvals.supplier||!s.approvals.students))throw Error('Le prochain menu doit être validé par tous');s.phase=Math.min(4,s.phase+1);s.hint=false;if(s.phase===3)s.approvals={supplier:false,students:false};}
  else throw Error('Action inconnue');return;
 }
 if(a.type==='menu'&&role==='manager'&&[1,3].includes(s.phase)){const c=cost(a.value,s.phase===3?s.event:null);if(s.phase===1&&a.value==='secours')throw Error('Réserve disponible au prochain repas');if(c>1500&&s.phase===1||s.phase===3&&c+s.first.cost>3000)throw Error('Budget dépassé');s[s.phase===1?'first':'second']={id:a.value,cost:c};s.approvals={supplier:false,students:false};}
 else if(a.type==='approve'&&[1,3].includes(s.phase)&&['supplier','students'].includes(role)){if(!s[s.phase===1?'first':'second'])throw Error('Attendez la proposition des gestionnaires');s.approvals[role]=true;}
 else if(a.type==='service'&&role==='students'&&s.phase===2){if(!services[a.value])throw Error('Service inconnu');s.service=a.value;s.measure=false;}
 else if(a.type==='measure'&&role==='manager'&&s.phase===2){if(!s.service)throw Error('Attendez le choix du service');const w=services[s.service].waste;if(Number(a.grams)!==w*1000/600||Number(a.percent)!==w/3)throw Error('Vérifiez les unités et les deux calculs');s.measure=true;}
 else throw Error('Action non disponible pour votre équipe');
}
export function view(s){return {...s,menus,services,remaining:3000-(s.first?.cost||0)-(s.second?.cost||0),waste:s.service?services[s.service].waste:null}}
