"""How data/alignment_final.json and data/resolution_log.json were made (run once, from 2026/literature/translators/:
python -m translators.resolve_passes). Every disagreement between pass 1 and pass 2 has one decision below, with
the rule it rests on (README, 'How we aligned'). Re-running gives the same two files.
"""
import json,sys,copy
sys.path.insert(0,'.')
from translators import versions as Vm, align
V=Vm.build()
p1=json.load(open('data/alignment_pass1.json')); p2=json.load(open('data/alignment_pass2.json'))
L1=align.resolve(p1,V); L2=align.resolve(p2,V)
diffs=align.compare(L1,L2)
R3b="R3b: a word that spells out a person or thing the Greek leaves implied goes with the Greek word that implies it"
R4b="R4b: when a version word matches one Greek word's sense and another's slot, it goes with the sense"
R2b="R2b: one version word may serve two Greek words when it fuses them (negation + verb)"
R5="R5: no link without a shared part of the Greek word's own meaning"
EPI="R3c: an added epithet (cold, immortal, wild) stays unlinked"
LSJ="LSJ gloss decides close vs loose"
D={
 ('catullus','greek:3:2'):('new',[["4:et"],"loose"],"R6: 'et' joins two verbs as καί does, but a different pair (spectat et audit vs sits and listens): same job, shifted -> loose"),
 ('catullus','greek:3:4'):('pass1',None,R4b+": dulce = ἆδυ 'sweetly', moved to the laughing"),
 ('catullus','greek:5:3'):('pass1',None,R4b+": 'Dulce' goes with ἆδυ, so ἰμερόεν has no counterpart"),
 ('catullus','greek:6:1'):('pass1',None,"LSJ καρδία includes the heart as seat of feelings and mind; 'sensus' keeps part of that -> loose link kept"),
 ('catullus','greek:6:4'):('pass2',None,R5+": eripit 'snatches away' shares no part of πτοέω 'terrify, flutter'"),
 ('catullus','greek:8:3'):('pass1',None,"LSJ cites this line under εἴκω 'it is allowable or possible'; 'est (super)' keeps the existential sense -> loose"),
 ('catullus','greek:11:5'):('pass2',None,"'sonitu' (with sound) shares the noise in 'make a buzzing noise' -> included, as in Symonds"),
 ('catullus','greek:12:2'):('pass1',None,"LSJ cites this very line under ἀκοή 'ear' -> close"),
 ('merivale','greek:2:4'):('pass2',None,"R4 loose: 'look on thee' stands in the slot of 'sits facing you' and keeps the facing; no other Greek word claims it"),
 ('merivale','greek:3:5'):('pass1',None,R3b+" ('thy' = the you who speaks)"),
 ('merivale','greek:5:2'):('pass2',None,"the repeated noun 'smile' restates the laughing verb; both passes agree it is not an addition of new content"),
 ('merivale','greek:5:3'):('pass2',None,"'sweet' sits in the slot of the adverb 'lovely', 'charm' carries its sense (LSJ 'charming')"),
 ('merivale','greek:5:4'):('pass1',None,"τό 'that' -> relative 'whose': function shifted -> loose"),
 ('merivale','greek:6:4'):('pass1',None,"R3: 'with' marks the means; LSJ πτοέω 'terrify, scare' = 'struck with alarm' -> close"),
 ('merivale','greek:7:6'):('pass2',None,"'Speechless' keeps voice/speech plus the negation -> close for φώνας (οὐδέν stays loose, both passes)"),
 ('merivale','greek:11:3'):('pass1',None,"'fail' carries the negation of 'I see nothing' (moved to the last line) -> loose"),
 ('merivale','greek:13:3'):('pass2',None,EPI+": 'cold'"),
 ('merivale','greek:14:1'):('new',[["14:every","14:limb"],"close"],R3b+" ('limb' spells out the implied 'me'); 'every' = 'all' -> close"),
 ('merivale','greek:15:2'):('pass1',None,R5+": 'fail' shares no part of 'be dead'"),
 ('merivale','greek:15:3'):('pass2',None,"R6: 'and' opens the last clause as δέ does -> close (as for Philips)"),
 ('philips','greek:2:4'):('pass1',None,R4b+": 'by' = near, the sense of πλησίον; ἐναντίος has no counterpart"),
 ('philips','greek:3:3'):('pass1',None,R4b),
 ('philips','greek:3:5'):('pass1',None,R3b+" ('thee' = the you who speaks)"),
 ('philips','greek:5:5'):('pass1',None,"R3: one Greek pronoun, one English pronoun: μοι -> the 'my' of 'my soul'; the 'my' of 'my breast' is added"),
 ('philips','greek:7:1'):('pass2',None,"'while' and 'when' are both temporal conjunctions -> close"),
 ('philips','greek:7:3'):('pass1',None,"'gaze' keeps 'see' (LSJ εἴδω 'see, perceive, behold') -> close"),
 ('philips','greek:8:1'):('pass1',None,R2b+": 'was lost' fuses 'nothing' and 'comes'"),
 ('philips','greek:8:3'):('new',[["8:was#2","8:lost"],"loose"],R2b),
 ('philips','greek:10:2'):('pass1',None,"LSJ χρώς includes 'one's body, frame' -> close"),
 ('philips','greek:12:2'):('pass1',None,"LSJ cites this very line under ἀκοή 'ear' -> close"),
 ('philips','greek:13:5'):('pass2',None,"'thrilled' (shivered) shares the trembling -> included, loose"),
 ('philips','greek:15:3'):('pass2',None,"R6: 'and' opens the death clause as δέ does -> close"),
 ('smollett','greek:6:3'):('pass1',None,"'bosom' = breast (LSJ στῆθος 'breast'); a word-level match, wherever it sits"),
 ('smollett','greek:7:1'):('pass2',None,"'while' and 'when' are both temporal conjunctions -> close"),
 ('smollett','greek:7:3'):('pass1',None,"'gaze' keeps 'see' -> close"),
 ('smollett','greek:9:6'):('pass1',None,"'soft' is the adjective on the flame in the slot of λεπτόν and shares 'delicate' (LSJ 'thin, fine, delicate') -> loose"),
 ('smollett','greek:10:2'):('pass1',None,"LSJ χρώς includes 'one's body, frame' -> close"),
 ('symonds','greek:3:3'):('pass1',None,R3b+" ('thee' after 'beside')"),
 ('symonds','greek:3:5'):('pass1',None,R3b),
 ('symonds','greek:5:2'):('pass2',None,"the cognate noun 'laughter' restates the laughing verb"),
 ('symonds','greek:8:1'):('pass1',None,R2b+": 'hushed' carries the negation"),
 ('symonds','greek:8:3'):('pass2',None,R2b+": 'is hushed' fuses 'nothing' and 'comes'"),
 ('symonds','greek:9:1'):('pass1',None,"R6: 'Yea' intensifies; it does not oppose as ἀλλά 'but' does"),
 ('symonds','greek:10:2'):('pass1',None,"LSJ χρώς 'flesh' -> close"),
 ('symonds','greek:11:5'):('pass2',None,"'roaring' shares the noise -> included"),
 ('symonds','greek:12:2'):('pass1',None,"LSJ cites this very line under ἀκοή 'ear' -> close"),
 ('symonds','greek:14:1'):('pass1',None,R3b+" ('limbs' spells out the implied 'me')"),
 ('wharton','greek:2:4'):('pass1',None,"LSJ ἐναντίος includes 'before'; 'in thy presence' = before you -> close"),
 ('wharton','greek:3:3'):('pass2',None,R3b+" ('to him')"),
 ('wharton','greek:3:5'):('pass1',None,R3b+" ('thy')"),
 ('wharton','greek:8:3'):('pass1',None,"LSJ cites this line under εἴκω 'it is allowable or possible'; 'I have ... left' keeps 'there is (no voice) any more' -> loose"),
 ('wharton','greek:11:4'):('pass2',None,"'have sight' = see, with a change of part of speech -> close"),
 ('wharton','greek:12:2'):('pass1',None,"LSJ cites this very line under ἀκοή 'ear' -> close"),
 ('wharton','greek:14:1'):('pass1',None,R3b+" ('my body')"),
 ('wharton','greek:15:2'):('pass1',None,R3b+" ('one')"),
 ('wharton','greek:16:2'):('pass1',None,R5+": 'in my madness' shares nothing with ἄλλος 'another'; open doubt: Wharton may be translating a different reading of this bracketed word"),
}
final=copy.deepcopy(p1); final['pass']='final'; final['made']='2026-10-08: pass 1, with every disagreement with pass 2 resolved as logged in resolution_log.json'
log=[]
words={v['id']:{t['id']:t['word'] for t in v['tokens']} for v in V['versions']}
g={t['id']:t['word'] for t in V['greek']['tokens']}
assert len(diffs)==len(D), (len(diffs),len(D))
for x in diffs:
    key=(x['version'],x['greek']); choice,entry,reason=D[key]
    fv=final['versions'][x['version']]
    if choice=='pass2':
        e=p2['versions'][x['version']].get(x['greek'])
        if e is None: fv.pop(x['greek'],None)
        else: fv[x['greek']]=e[:2]
    elif choice=='new':
        fv[x['greek']]=entry
    f=lambda s: None if s is None else {"words":' '.join(words[x['version']][i] for i in s[0]),"strength":s[1]}
    log.append({"version":x['version'],"greek":x['greek'],"greek_word":g[x['greek']],"pass1":f(x['pass1']),"pass2":f(x['pass2']),"decision":choice,"reason":reason})
LF=align.resolve(final,V)
for x in log:
    l=LF[x['version']].get(x['greek']); x['final']=None if l is None else {"words":' '.join(words[x['version']][i] for i in sorted(l['to'],key=lambda t:[k for k in words[x['version']]].index(t))),"strength":l['strength']}
json.dump(final,open('data/alignment_final.json','w'),ensure_ascii=False,indent=1)
n=6*71
json.dump({"about":"Every (version, Greek word) where the two passes disagreed, the decision and the rule it rests on. Rules: README 'How we aligned'.",
 "decisions_compared":"6 versions x 71 Greek words = 426 (Catullus lines 13-16 have no aligned Greek words in either pass)",
 "disagreements":len(log),"agreement_share":round((n-len(log))/n,3),
 "decisions":{"pass1":sum(1 for x in log if x['decision']=='pass1'),"pass2":sum(1 for x in log if x['decision']=='pass2'),"new":sum(1 for x in log if x['decision']=='new')},
 "log":log},open('data/resolution_log.json','w'),ensure_ascii=False,indent=1)
print(len(log),(n-len(log))/n)
