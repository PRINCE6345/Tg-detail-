import os, json, requests
from datetime import date
from flask import Flask, request

BOT_TOKEN  = '8550444265:AAGo_g1hoBEsCYZhKsjy8uhc0UmtSwb8agE'
ADMIN_ID   = '6021592483'
CHANNEL    = '@princexhitmanmods'
CH_URL     = 'https://t.me/princexhitmanmods'
TG_URL     = 'https://api.telegram.org/bot' + BOT_TOKEN
SMS_URL    = 'https://ayaanmods.site/sms.php'
SMS_KEY    = 'annonymoussms'
NUM_URL    = 'https://anon-num-info.vercel.app/num'
NUM_KEY    = 'numt0605'
ADH_URL    = 'https://anon-num-info.vercel.app/aadhar'
ADH_KEY    = 'tempad705'
DB         = 'db.json'
CODES      = 'codes.json'

app = Flask(__name__)

# ── DB ──────────────────────────────────────────────
def rdb():
    return json.load(open(DB)) if os.path.exists(DB) else {}

def wdb(d):
    json.dump(d, open(DB,'w'), indent=2)

def user(d, uid, name=''):
    uid = str(uid)
    if uid not in d:
        d[uid] = {'name':name,'pts':5,'daily':'','ref':None,'refs':[],
                  'searches':0,'wait':None,'ok':False}
    return d[uid]

def rcodes():
    return json.load(open(CODES)) if os.path.exists(CODES) else {}

def wcodes(c):
    json.dump(c, open(CODES,'w'), indent=2)

# ── TG ──────────────────────────────────────────────
def tg(m, d):
    try: return requests.post(f'{TG_URL}/{m}', json=d, timeout=20).json()
    except: return {}

def send(cid, txt, kb=None):
    p = {'chat_id':cid,'text':txt,'parse_mode':'HTML','disable_web_page_preview':True}
    if kb: p['reply_markup'] = {'inline_keyboard': kb}
    tg('sendMessage', p)

def action(cid):
    tg('sendChatAction', {'chat_id':cid,'action':'typing'})

# ── KEYBOARDS ───────────────────────────────────────
def mkb():
    return [
        [{'text':'📱 Number Lookup','callback_data':'num'},
         {'text':'🪪 Aadhaar Lookup','callback_data':'adh'}],
        [{'text':'📡 TG to Number','callback_data':'tgnum'}],
        [{'text':'👤 Profile','callback_data':'prof'},
         {'text':'🎁 Daily Bonus','callback_data':'daily'}],
        [{'text':'🔗 Refer & Earn','callback_data':'refer'},
         {'text':'🎟 Promo Code','callback_data':'promo'}],
        [{'text':'📢 Channel','url':CH_URL},
         {'text':'📊 Stats','callback_data':'stats'}],
    ]

def bkb():
    return [[{'text':'🏠 Back to Menu','callback_data':'menu'}]]

def skb():
    return [
        [{'text':'📱 Number Lookup','callback_data':'num'},
         {'text':'🪪 Aadhaar Lookup','callback_data':'adh'}],
        [{'text':'📡 TG to Number','callback_data':'tgnum'},
         {'text':'🏠 Menu','callback_data':'menu'}],
    ]

# ── MESSAGES ────────────────────────────────────────
def join_msg():
    return (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "  ⛔ <b>ACCESS DENIED</b> ⛔\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔐 Join our channel to unlock\n"
        "<b>HITMAN OSINT BOT!</b>\n\n"
        "┣ 📱 Number Info Lookup\n"
        "┣ 🪪 Aadhaar Info Lookup\n"
        "┣ 📡 TG Username to Number\n"
        "┣ 💎 5 Free Points on join\n"
        "┗ 🎁 Daily Bonus + Referrals\n\n"
        "<i>Join then tap ✅ button!</i>"
    )

def home_msg(name, pts):
    return (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "  💀 <b>HITMAN OSINT BOT</b> 💀\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 <b>Hey {name}!</b>\n\n"
        "🔍 <b>Available Tools:</b>\n"
        "┣ 📱 <b>Number Lookup</b>\n"
        "┣ 🪪 <b>Aadhaar Lookup</b>\n"
        "┗ 📡 <b>TG Username → Number</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Balance: {pts} pts</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 Choose a tool below!"
    )

# ── API HELPERS ──────────────────────────────────────
def fix_addr(a):
    if not a: return None
    parts = [x.strip() for x in str(a).split('!') if x.strip()]
    return ', '.join(parts) if parts else None

SKIP = {'developer','dev','owner','api_owner','channel','channel_link','note',
        'credits','powered_by','source','provider','success','msg','message',
        'code','status','service','cached','proxyused','attempt','input_type',
        'input_value','credit'}

ICONS = {
    'name':'👤','fname':'👥','num':'📱','alt':'📞',
    'aadhar':'🪪','circle':'📡','address':'📍',
    'email':'📧','dob':'🎂','gender':'⚧','state':'🗺',
    'city':'🏙','number':'📱','tg_id':'🆔',
    'country':'🌍','country_code':'🔢',
}

LABELS = {
    'name':'Name','fname':'Father','num':'Number','alt':'Alt Number',
    'aadhar':'Aadhaar','circle':'Carrier/Circle','address':'Address',
    'email':'Email','dob':'Date of Birth','gender':'Gender',
    'state':'State','city':'City','number':'Phone','tg_id':'TG ID',
    'country':'Country','country_code':'Code',
}

def get_records(data):
    if not isinstance(data, dict): return []
    arr = None
    resp = data.get('response', {})
    if isinstance(resp, dict):
        arr = resp.get('data')
    if not arr:
        arr = data.get('data')
    if not arr or not isinstance(arr, list): return []
    seen = set()
    out = []
    for rec in arr:
        if not isinstance(rec, dict): continue
        sig = str(rec.get('num','')) + str(rec.get('name','')) + str(rec.get('aadhar',''))
        if sig in seen: continue
        seen.add(sig)
        clean = {}
        for k, v in rec.items():
            if k.lower() in SKIP: continue
            if v is None or str(v).strip() in ('', 'null', 'None'): continue
            if k == 'address':
                v = fix_addr(v)
                if not v: continue
            clean[k] = v
        if clean: out.append(clean)
    return out

def fmt_records(records):
    if not records:
        return "⚠️ <i>No details found</i>\n"
    lines = ""
    for i, rec in enumerate(records[:5], 1):
        if len(records) > 1:
            lines += f"\n<b>── Record {i} ──────────────</b>\n"
        for k, v in rec.items():
            icon  = ICONS.get(k, '▸')
            label = LABELS.get(k, k.upper())
            lines += f"{icon} <b>{label}:</b> <code>{v}</code>\n"
    return lines

# ── SEARCH FUNCTIONS ─────────────────────────────────
def no_pts_msg(cid):
    send(cid,
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "  😔 <b>OUT OF POINTS!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "You need at least <b>1 point</b>!\n\n"
        "┣ 🎁 Daily Bonus → +2 pts\n"
        "┣ 🔗 Refer Friend → +5 pts\n"
        "┗ 🎟 Promo Code → Variable",
        [[{'text':'🎁 Daily','callback_data':'daily'},
          {'text':'🔗 Refer','callback_data':'refer'}]]
    )

def do_num(cid, uid, number, d):
    if d[uid]['pts'] < 1: no_pts_msg(cid); return
    action(cid)
    num = number.replace('+','').replace(' ','').replace('-','')
    if len(num) > 10 and num.startswith('91'): num = num[2:]
    try:
        r = requests.get(f"{NUM_URL}?key={NUM_KEY}&num={num}", timeout=15)
        res = r.json() if r.status_code == 200 else None
    except: res = None
    d[uid]['pts'] -= 1
    d[uid]['searches'] += 1
    pts = d[uid]['pts']
    wdb(d)
    recs = get_records(res) if res else []
    if not recs:
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "  ❌ <b>NO DATA FOUND</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📱 <b>Number:</b> <code>{number}</code>\n\n"
            f"💎 Points left: <b>{pts}</b>", skb()); return
    send(cid,
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "  ✅ <b>DATA RETRIEVED!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📱 <b>Query:</b> <code>{number}</code>\n"
        f"📊 <b>Records found:</b> {len(recs)}\n\n"
        + fmt_records(recs) +
        f"\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Points left: {pts}</b>\n"
        "🤖 <b>Made by PRINCE</b>", skb())

def do_adh(cid, uid, aid, d):
    if d[uid]['pts'] < 1: no_pts_msg(cid); return
    action(cid)
    try:
        r = requests.get(f"{ADH_URL}?key={ADH_KEY}&id={aid}", timeout=15)
        res = r.json() if r.status_code == 200 else None
    except: res = None
    d[uid]['pts'] -= 1
    d[uid]['searches'] += 1
    pts = d[uid]['pts']
    wdb(d)
    recs = get_records(res) if res else []
    if not recs:
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "  ❌ <b>NO DATA FOUND</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🪪 <b>Aadhaar:</b> <code>{aid}</code>\n\n"
            f"💎 Points left: <b>{pts}</b>", skb()); return
    send(cid,
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "  ✅ <b>DATA RETRIEVED!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🪪 <b>Aadhaar:</b> <code>{aid}</code>\n"
        f"📊 <b>Records found:</b> {len(recs)}\n\n"
        + fmt_records(recs) +
        f"\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Points left: {pts}</b>\n"
        "🤖 <b>Made by PRINCE</b>", skb())

def do_tgnum(cid, uid, term, d):
    if d[uid]['pts'] < 1: no_pts_msg(cid); return
    action(cid)
    t = term.lstrip('@')
    try:
        r = requests.get(f"{SMS_URL}?key={SMS_KEY}&term={t}", timeout=15)
        res = r.json() if r.status_code == 200 else None
    except: res = None
    d[uid]['pts'] -= 1
    d[uid]['searches'] += 1
    pts = d[uid]['pts']
    wdb(d)
    if not res or not res.get('success'):
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "  ❌ <b>NO DATA FOUND</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📡 <b>Target:</b> <code>{term}</code>\n\n"
            f"💎 Points left: <b>{pts}</b>", skb()); return
    result = res.get('result', {})
    number = result.get('number','')
    tgid   = result.get('tg_id','')
    cc     = result.get('country_code','')
    cntry  = result.get('country','')
    # fetch num details
    recs = []
    if number:
        try:
            r2 = requests.get(f"{NUM_URL}?key={NUM_KEY}&num={number}", timeout=15)
            if r2.status_code == 200:
                recs = get_records(r2.json())
        except: pass
    msg = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "  ✅ <b>DATA RETRIEVED!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📡 <b>Target:</b> <code>{term}</code>\n"
        f"🆔 <b>TG ID:</b> <code>{tgid}</code>\n"
        f"📱 <b>Phone:</b> <code>{cc}{number}</code>\n"
        f"🌍 <b>Country:</b> {cntry}\n"
    )
    if recs:
        msg += "\n📋 <b>Number Details:</b>\n"
        msg += fmt_records(recs)
    msg += (
        f"\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Points left: {pts}</b>\n"
        "🤖 <b>Made by PRINCE</b>"
    )
    send(cid, msg, skb())

# ── CALLBACKS ────────────────────────────────────────
def on_cb(cb):
    cid  = cb['message']['chat']['id']
    uid  = str(cb['from']['id'])
    name = cb['from'].get('first_name', 'User')
    data = cb['data']
    tg('answerCallbackQuery', {'callback_query_id': cb['id']})
    d = rdb()
    user(d, uid, name)
    d[uid]['name'] = name

    if data == 'check_join':
        d[uid]['ok'] = True; wdb(d)
        send(cid,
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"  🎊 <b>WELCOME {name}!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ <b>Access Granted!</b>\n"
            "💎 <b>5 Free Points</b> added!\n\n"
            "Choose a tool below 👇", mkb())

    elif data == 'num':
        d[uid]['wait'] = 'num'; wdb(d)
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "  📱 <b>NUMBER LOOKUP</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Send a mobile number:\n"
            "<i>Example: <code>6205923286</code></i>\n\n"
            "💎 Cost: <b>1 Point</b>",
            [[{'text':'❌ Cancel','callback_data':'menu'}]])

    elif data == 'adh':
        d[uid]['wait'] = 'adh'; wdb(d)
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "  🪪 <b>AADHAAR LOOKUP</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Send a 12-digit Aadhaar number:\n"
            "<i>Example: <code>327567544017</code></i>\n\n"
            "💎 Cost: <b>1 Point</b>",
            [[{'text':'❌ Cancel','callback_data':'menu'}]])

    elif data == 'tgnum':
        d[uid]['wait'] = 'tgnum'; wdb(d)
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "  📡 <b>TG → NUMBER</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Send a Telegram @username:\n"
            "<i>Example: <code>@durov</code></i>\n\n"
            "💎 Cost: <b>1 Point</b>",
            [[{'text':'❌ Cancel','callback_data':'menu'}]])

    elif data == 'daily':
        today = str(date.today())
        if d[uid]['daily'] == today:
            send(cid,
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "  🎁 <b>DAILY BONUS</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "✅ Already claimed today!\n\n"
                f"💎 Balance: <b>{d[uid]['pts']} pts</b>\n"
                "🕐 Come back tomorrow!", bkb())
        else:
            d[uid]['pts'] += 2
            d[uid]['daily'] = today; wdb(d)
            send(cid,
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "  ✨ <b>BONUS CLAIMED!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🟢 <b>+2 Points</b> added!\n"
                f"💎 Balance: <b>{d[uid]['pts']} pts</b>\n\n"
                "🔥 Come back tomorrow!", bkb())

    elif data == 'prof':
        u = d[uid]
        pts = u['pts']
        rank = ('💀 LEGEND' if pts>=500 else '👑 VIP' if pts>=100
                else '🥇 Gold' if pts>=50 else '🥈 Silver' if pts>=20 else '🥉 Bronze')
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "     👤 <b>MY PROFILE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"👋 <b>Name:</b> {u['name']}\n"
            f"🏅 <b>Rank:</b> {rank}\n"
            f"💎 <b>Balance:</b> {pts} pts\n"
            f"🔎 <b>Searches:</b> {u['searches']}\n"
            f"👥 <b>Referrals:</b> {len(u.get('refs',[]))}\n\n"
            "🤖 <b>Made by PRINCE</b>", bkb())

    elif data == 'refer':
        r = tg('getMe', {})
        bun = r.get('result', {}).get('username', 'HitmanOsintBot')
        link = f"https://t.me/{bun}?start=ref_{uid}"
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "   💰 <b>REFER & EARN</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎁 Each referral = <b>+5 Points</b>\n\n"
            "📲 <b>Your Link:</b>\n"
            f"<code>{link}</code>\n\n"
            f"💎 Balance: <b>{d[uid]['pts']} pts</b>", bkb())

    elif data == 'promo':
        d[uid]['wait'] = 'promo'; wdb(d)
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "  🎟 <b>REDEEM PROMO</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Send your promo code:\n"
            "<i>Example: PRINCE50</i>",
            [[{'text':'❌ Cancel','callback_data':'menu'}]])

    elif data == 'stats':
        db2 = rdb()
        ts = sum(u.get('searches',0) for u in db2.values())
        send(cid,
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "   📊 <b>BOT STATS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 <b>Total Users:</b> {len(db2)}\n"
            f"🔎 <b>Total Searches:</b> {ts}\n\n"
            "🤖 <b>Made by PRINCE</b>", bkb())

    elif data == 'menu':
        d[uid]['wait'] = None; wdb(d)
        send(cid, home_msg(name, d[uid]['pts']), mkb())

    wdb(d)

# ── MESSAGES ─────────────────────────────────────────
def on_msg(msg):
    cid  = msg['chat']['id']
    uid  = str(msg['from']['id'])
    name = msg['from'].get('first_name', 'User')
    text = msg.get('text', '').strip()
    d    = rdb()
    user(d, uid, name)
    d[uid]['name'] = name

    if text.startswith('/start'):
        parts = text.split()
        if len(parts) > 1 and parts[1].startswith('ref_'):
            rb = parts[1][4:]
            if rb != uid and not d[uid].get('ref'):
                d[uid]['ref'] = rb
                user(d, rb)
                if uid not in d[rb].get('refs', []):
                    d[rb]['refs'].append(uid)
                    d[rb]['pts'] += 5
                    tg('sendMessage', {
                        'chat_id': rb,
                        'text': (f"🔗 <b>NEW REFERRAL!</b>\n"
                                 f"👤 <b>{name}</b> joined!\n"
                                 f"🟢 <b>+5 Points</b> added!\n"
                                 f"💎 Balance: <b>{d[rb]['pts']} pts</b>"),
                        'parse_mode': 'HTML'
                    })
        wdb(d)
        if d[uid].get('ok'):
            send(cid, home_msg(name, d[uid]['pts']), mkb())
        else:
            send(cid, join_msg(), [
                [{'text':'📢 Join Channel','url':CH_URL}],
                [{'text':'✅ Joined! Check','callback_data':'check_join'}]
            ])
        return

    if not d[uid].get('ok'):
        send(cid, join_msg(), [
            [{'text':'📢 Join Channel','url':CH_URL}],
            [{'text':'✅ Joined! Check','callback_data':'check_join'}]
        ])
        wdb(d); return

    wait = d[uid].get('wait')

    if wait == 'promo':
        d[uid]['wait'] = None
        codes = rcodes()
        code  = text.upper().strip()
        if code in codes:
            if uid in codes[code].get('used', []):
                send(cid, "⚠️ <b>Already used this code!</b>", bkb())
            else:
                pts = int(codes[code]['points'])
                d[uid]['pts'] += pts
                codes[code]['used'].append(uid)
                wcodes(codes)
                send(cid,
                    f"🎊 <b>CODE REDEEMED!</b>\n\n"
                    f"🎟 Code: <code>{code}</code>\n"
                    f"🟢 <b>+{pts} Points</b> added!\n"
                    f"💎 Balance: <b>{d[uid]['pts']} pts</b>", bkb())
        else:
            send(cid, "🚫 <b>Invalid code!</b>", bkb())
        wdb(d); return

    if wait == 'num':
        d[uid]['wait'] = None; wdb(d)
        num = text.replace('+','').replace(' ','').replace('-','')
        if not num.isdigit() or len(num) < 10:
            send(cid, "❗ Invalid number!\n<i>Example: <code>6205923286</code></i>",
                 [[{'text':'🔄 Try Again','callback_data':'num'},
                   {'text':'🏠 Menu','callback_data':'menu'}]])
            return
        do_num(cid, uid, text, d); return

    if wait == 'adh':
        d[uid]['wait'] = None; wdb(d)
        aid = text.replace(' ','').replace('-','')
        if not aid.isdigit() or len(aid) != 12:
            send(cid, "❗ Invalid Aadhaar! Must be 12 digits.\n<i>Example: <code>327567544017</code></i>",
                 [[{'text':'🔄 Try Again','callback_data':'adh'},
                   {'text':'🏠 Menu','callback_data':'menu'}]])
            return
        do_adh(cid, uid, aid, d); return

    if wait == 'tgnum':
        d[uid]['wait'] = None; wdb(d)
        if len(text.lstrip('@')) < 3:
            send(cid, "❗ Invalid username!\n<i>Example: <code>@durov</code></i>",
                 [[{'text':'🔄 Try Again','callback_data':'tgnum'},
                   {'text':'🏠 Menu','callback_data':'menu'}]])
            return
        do_tgnum(cid, uid, text, d); return

    if uid == ADMIN_ID:
        if text.startswith('/addcode '):
            p = text.split()
            if len(p) == 3:
                c = rcodes(); c[p[1].upper()] = {'points':int(p[2]),'used':[]}; wcodes(c)
                send(cid, f"✅ Code <code>{p[1].upper()}</code> = 💎 <b>{p[2]} pts</b>")
            wdb(d); return
        if text.startswith('/delcode '):
            code = text.split()[1].upper(); c = rcodes()
            if code in c: del c[code]; wcodes(c); send(cid, f"🗑 <code>{code}</code> deleted!")
            else: send(cid, "❌ Not found!")
            wdb(d); return
        if text.startswith('/addpoints '):
            p = text.split()
            if len(p) == 3:
                user(d, p[1]); d[p[1]]['pts'] += int(p[2]); wdb(d)
                send(cid, f"✅ Added 💎 <b>{p[2]} pts</b> to <code>{p[1]}</code>!")
            return
        if text == '/stats':
            ts = sum(u.get('searches',0) for u in d.values())
            send(cid, f"📊 <b>STATS</b>\n\n👥 Users: <b>{len(d)}</b>\n🔎 Searches: <b>{ts}</b>")
            wdb(d); return
        if text.startswith('/broadcast '):
            bmsg = text[11:]; sent = 0
            for bid in list(d.keys()):
                try:
                    if tg('sendMessage',{'chat_id':bid,'text':f"📣 <b>ANNOUNCEMENT</b>\n\n{bmsg}\n\n🤖 <b>Made by PRINCE</b>",'parse_mode':'HTML'}).get('ok'): sent+=1
                except: pass
            send(cid, f"📢 Sent to <b>{sent}</b> users!"); wdb(d); return
        if text == '/listcodes':
            c = rcodes()
            if not c: send(cid, "❌ No active codes.")
            else:
                lines = "🎟 <b>Active Codes:</b>\n\n"
                for k,v in c.items(): lines += f"┣ <code>{k}</code> — 💎 {v['points']} pts | Used: {len(v.get('used',[]))}x\n"
                send(cid, lines)
            wdb(d); return

    send(cid, home_msg(name, d[uid]['pts']), mkb())
    wdb(d)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    data = request.get_json()
    if not data: return 'ok'
    if 'callback_query' in data: on_cb(data['callback_query'])
    elif 'message' in data: on_msg(data['message'])
    return 'ok'

@app.route('/')
def index(): return '💀 HITMAN OSINT BOT - Made by PRINCE'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
