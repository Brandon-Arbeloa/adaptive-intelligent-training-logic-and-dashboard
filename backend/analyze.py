from families import EXERCISE_FAMILIES, MUSCLE_TO_FAMILIES
from config import OVERUSED, BALANCED_MIN

def parse_rows(week_name, rows):
    """Parse rows from Week sheets - columns B (muscle) and C (exercise)"""
    wk = int(week_name.split()[-1])
    out = []
    for r in rows:
        # We're getting B2:E, so:
        # Index 0 = Column B (Muscle Group)
        # Index 1 = Column C (Exercise)
        # Index 2 = Column D (weird dates, ignore)
        # Index 3 = Column E (weird dates, ignore)
        
        if len(r) < 2:
            continue
            
        mg = r[0] if len(r) > 0 else ""
        ex = r[1] if len(r) > 1 else ""
        
        # Clean exercise name
        ex = str(ex).strip() if ex else ""
        if not ex:
            continue
            
        # Skip if it's a number row (like "6 6 6" in your data)
        try:
            float(ex)
            continue  # Skip numeric values
        except:
            pass
        
        out.append({
            'week': wk,
            'muscleGroup': str(mg).strip() if mg else 'Unknown',
            'exercise': ex,
            'volume': 1  # Just count presence for rotation analysis
        })
    return out

def build_db(rows):
    db={}
    for r in rows:
        ex=r['exercise']; e=db.get(ex)
        if not e: e=db.setdefault(ex, {'muscleGroup':r['muscleGroup'],'weeks':set(),'totalVolume':0.0})
        e['weeks'].add(r['week']); e['totalVolume']+=r['volume']
    for ex,e in db.items(): e['frequency']=len(e['weeks'])
    return db

def _alts(exercise, mg):
    tgt=exercise.lower(); out=[]
    for fam, exs in EXERCISE_FAMILIES.items():
        exs_l=[x.lower() for x in exs]
        if tgt in exs_l:
            out += [(alt,0.9,f'Same pattern ({fam})') for alt in exs if alt.lower()!=tgt]
    if not out and mg:
        for fam in MUSCLE_TO_FAMILIES.get(mg, []):
            out += [(alt,0.6,f'Same muscle group ({mg})') for alt in EXERCISE_FAMILIES.get(fam,[])]
    return sorted(out, key=lambda t: t[1], reverse=True)[:5]

def analyze(db):
    over, bal, under, ideas = [], [], [], []
    for ex, info in db.items():
        f=info['frequency']; mg=info['muscleGroup'] or 'Unknown'
        if f>=OVERUSED:
            al=_alts(ex, mg); over.append((ex,f,al,'high' if f>=6 else 'medium'))
            if al: ideas.append(f'Replace "{ex}" (used {f} weeks) → "{al[0][0]}" ({al[0][2]})')
        elif f>=BALANCED_MIN:
            bal.append((ex,f))
        else:
            under.append((ex,f))
    over.sort(key=lambda t:(-t[1], t[0].lower()))
    bal.sort(key=lambda t:(-t[1], t[0].lower()))
    under.sort(key=lambda t:(t[1], t[0].lower()))
    return over, bal, under, ideas

def report_lines(db, over, bal, under, ideas, timestamp):
    lines=['📊 SUMMARY','',
           f'• Total exercises: {len(db)}',
           f'• Overused (>= {OVERUSED} wks): {len(over)}',
           f'• Balanced ({BALANCED_MIN}–{OVERUSED-1} wks): {len(bal)}',
           f'• Underused / New: {len(under)}','']
    if over:
        lines.append('🚨 ROTATION PRIORITY:')
        for ex,f,al,urg in over[:10]:
            emoji='🔥' if urg=='high' else '⚠️'
            swap=f' → {al[0][0]}' if al else ''
            lines.append(f'{emoji} {ex} ({f} wks){swap}')
        lines.append('')
    if ideas:
        lines.append('💡 SMART IDEAS:')
        for s in ideas[:10]: lines.append(f'• {s}')
        lines.append('')
    if bal:
        lines.append('✅ WELL-BALANCED:')
        for ex,f in bal[:10]: lines.append(f'• {ex} ({f} wks)')
        lines.append('')
    lines.append(f'Last updated: {timestamp}')
    return lines