import os
import json
import requests
from datetime import date
from flask import Flask, request

BOT_TOKEN   = '8550444265:AAGo_g1hoBEsCYZhKsjy8uhc0UmtSwb8agE'
CHANNEL     = '@princexhitmanmods'
CHANNEL_URL = 'https://t.me/princexhitmanmods'
NUM_API     = 'https://anon-num-info.vercel.app/num'
NUM_KEY     = 'num3004'
AADHAR_API  = 'https://anon-num-info.vercel.app/aadhar'
AADHAR_KEY  = 'temp3004'
ADMIN_ID    = '6021592483'
TG_API      = f'https://api.telegram.org/bot{BOT_TOKEN}'
DB_FILE     = 'users_db.json'
CODES_FILE  = 'promo_codes.json'

app = Flask(__name__)

def load_db():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE) as f: return json.load(f)

def save_db(db):
    with open(DB_FILE,'w') as f: json.dump(db,f,indent=2)

def get_user(db,uid,name=''):
    uid=str(uid)
    if uid not in db:
        db[uid]={'name':name,'points':5,'last_daily':'','referred_by':None,
                 'referrals':[],'searches':0,'awaiting':None,'joined':False}
    return db[uid]

def load_codes():
    if not os.path.exists(CODES_FILE): return {}
    with open(CODES_FILE) as f: return json.load(f)

def save_codes(c):
    with open(CODES_FILE,'w') as f: json.dump(c,f,indent=2)

def tg(method,data):
    try: return requests.post(f'{TG_API}/{method}',json=data,timeout=20).json()
    except: return {}

def send(cid,text,kb=None):
    d={'chat_id':cid,'text':text,'parse_mode':'HTML','disable_web_page_preview':True}
    if kb: d['reply_markup']={'inline_keyboard':kb}
    return tg('sendMessage',d)

def typing(cid): tg('sendChatAction',{'chat_id':cid,'action':'typing'})

def main_kb():
    return [
        [{'text':'\U0001f4f1 \U0001d5a1\U0001d5ce\U0001d5ba\U0001d5af\U0001d5ee\U0001d5ff \U0001d5df\U0001d5f2\U0001d5f2\U0001d5f8\U0001d5ee\U0001d5fd','callback_data':'num_search'},
         {'text':'\U0001faaa \U0001d41a\U0001d41a\U0001d41d\U0001d421\U0001d41a\U0001d41a\U0001d42b \U0001d41f\U0001d428\U0001d428\U0001d424\U0001d42e\U0001d429','callback_data':'aadhar_search'}],
        [{'text':'\U0001f464 \U0001d40c\U0001d418 \U0001d40f\U0001d42b\U0001d428\U0001d41f\U0001d422\U0001d425\U0001d41e','callback_data':'profile'},
         {'text':'\U0001f381 \U0001d403\U0001d41a\U0001d422\U0001d425\U0001d418 \U0001d401\U0001d428\U0001d427\U0001d42e\U0001d42c','callback_data':'daily'}],
        [{'text':'\U0001f517 \U0001d411\U0001d41e\U0001d41f\U0001d41e\U0001d42b & \U0001d402\U0001d41a\U0001d42b\U0001d427','callback_data':'refer'},
         {'text':'\U0001f39f\ufe0f \U0001d40f\U0001d42b\U0001d428\U0001d426\U0001d428 \U0001d402\U0001d428\U0001d41d\U0001d41e','callback_data':'redeem'}],
        [{'text':'\U0001f4ca \U0001d412\U0001d42d\U0001d41a\U0001d42d\U0001d42c','callback_data':'botstats'},
         {'text':'\U0001f4e2 \U0001d402\U0001d421\U0001d41a\U0001d427\U0001d427\U0001d41e\U0001d425','url':CHANNEL_URL}],
    ]

def menu_kb(): return [[{'text':'\U0001f3e0 \u00ab Back','callback_data':'menu'}]]

def search_kb():
    return [[{'text':'\U0001f4f1 Number Search','callback_data':'num_search'},
             {'text':'\U0001faaa Aadhaar Search','callback_data':'aadhar_search'}],
            [{'text':'\U0001f3e0 Menu','callback_data':'menu'}]]

def clean_addr(a):
    if not a: return None
    p=[x.strip() for x in a.split('!') if x.strip()]
    return ', '.join(p) if p else None

def parse_records(data):
    arr=None
    if isinstance(data,dict):
        resp=data.get('response',{})
        if isinstance(resp,dict): arr=resp.get('data',[])
        if not arr: arr=data.get('data',[])
    if not arr or not isinstance(arr,list): return []
    SKIP={'developer','dev','owner','api_owner','channel','channel_link','note',
          'credits','powered_by','source','provider','success','msg','message',
          'code','status','service'}
    seen=set(); records=[]
    for rec in arr:
        if not isinstance(rec,dict): continue
        sig=f"{rec.get('num','')}{rec.get('name','')}{rec.get('aadhar','')}"
        if sig in seen: continue
        seen.add(sig)
        clean={}
        for k,v in rec.items():
            if k.lower() in SKIP: continue
            if v is None or str(v).strip() in ('','null'): continue
            if k=='address':
                v=clean_addr(str(v))
                if not v: continue
            clean[k]=v
        if clean: records.append(clean)
    return records

def format_records(records):
    if not records: return "\u26a0\ufe0f <i>No details found</i>"
    FM={'name':('\U0001f464','Name'),'fname':('\U0001f465','Father'),
        'num':('\U0001f4f1','Number'),'alt':('\U0001f4de','Alt Num'),
        'aadhar':('\U0001faaa','Aadhaar'),'circle':('\U0001f4e1','Circle'),
        'address':('\U0001f4cd','Address'),'email':('\U0001f4e7','Email'),
        'dob':('\U0001f382','DOB'),'gender':('\u26a7','Gender'),
        'state':('\U0001f5fa\ufe0f','State'),'city':('\U0001f3d9\ufe0f','City')}
    lines=""
    for i,rec in enumerate(records[:5],1):
        if len(records)>1: lines+=f"\n\u250c\u2500\u2500 Record {i} \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        for k,v in rec.items():
            icon,label=FM.get(k,('\u25b8',k.upper()))
            lines+=f"\u2523 {icon} <b>{label}:</b>  <code>{v}</code>\n"
        if len(records)>1: lines+="\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
    return lines

def not_joined_msg():
    return ("\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "   \u26d4\ufe0f <b>ACCESS DENIED</b> \u26d4\ufe0f\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
            "\U0001f510 <b>Join our Official Channel\nto unlock this Elite OSINT Bot!</b>\n\n"
            "\u2728 <b>What you\'ll get:</b>\n"
            "\u2523 \U0001f4f1 Number \u2192 Full Info Lookup\n"
            "\u2523 \U0001faaa Aadhaar \u2192 Full Info Lookup\n"
            "\u2523 \U0001f48e 5 Free Starting Points\n"
            "\u2523 \U0001f381 Daily Bonus Rewards\n"
            "\u2517 \U0001f517 Referral Earning System\n\n"
            "<i>Tap \u2705 button after joining!</i>")

def welcome_msg(name,pts):
    return (f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"  \U0001f480 <b>HITMAN OSINT BOT</b> \U0001f480\n"
            f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
            f"\U0001f44b <b>Hey, {name}!</b>\n\n"
            f"\U0001f50d <b>Available Tools:</b>\n"
            f"\u2523 \U0001f4f1 <b>Number Lookup</b> \u2014 Full details\n"
            f"\u2517 \U0001faaa <b>Aadhaar Lookup</b> \u2014 Full details\n\n"
            f"\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\n"
            f"\U0001f4b0 <b>Balance:</b>  \U0001f48e <b>{pts} pts</b>\n"
            f"\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\u2504\n\n"
            f"\U0001f447 <b>Choose a tool below!</b>")

def do_num_search(cid,uid,number,db):
    if db[uid]['points']<1:
        send(cid,"\u2501"*21+"\n   \U0001f614 <b>OUT OF POINTS!</b>\n"+"\u2501"*21+"\n\nYou need <b>1 point</b>!\n\n\u2523 \U0001f381 Daily +2pts\n\u2517 \U0001f517 Refer +5pts",
             [[{'text':'\U0001f381 Daily','callback_data':'daily'},{'text':'\U0001f517 Refer','callback_data':'refer'}]]); return
    typing(cid)
    num=number.replace('+','').replace(' ','').replace('-','')
    if len(num)>10 and num.startswith('91'): num=num[2:]
    try:
        r=requests.get(f"{NUM_API}?key={NUM_KEY}&num={num}",timeout=15)
        res=r.json() if r.status_code==200 else None
    except: res=None
    db[uid]['points']-=1; db[uid]['searches']+=1
    pts_left=db[uid]['points']; save_db(db)
    records=parse_records(res) if res else []
    if not records:
        send(cid,f"\u2501"*21+"\n  \u274c <b>NO DATA FOUND!</b> \u274c\n"+"\u2501"*21+f"\n\n\U0001f4f1 <b>Number:</b> <code>{number}</code>\n\n\U0001f48e <b>Points Left:</b> {pts_left}",search_kb()); return
    send(cid,
        "\u2501"*21+"\n  \u2705 <b>DATA RETRIEVED!</b> \u2705\n"+"\u2501"*21+
        f"\n\n\U0001f4f1 <b>Query:</b> <code>{number}</code>\n"
        f"\U0001f4ca <b>Records:</b> {len(records)} found\n\n"+
        format_records(records)+
        "\n\u2504"*19+"\n\U0001f48e <b>Points Left:</b> "+str(pts_left)+"\n\U0001f916 <b>Made by PRINCE</b>\n"+"\u2501"*21,
        search_kb())

def do_aadhar_search(cid,uid,aid,db):
    if db[uid]['points']<1:
        PRINCE''id,"\u2501"*21+"\n   \U0001f614 <b>OUT OF POINTS!</b>\n"+"\u2501"*21+"\n\nYou need <b>1 point</b>!",
             [[{'text':'\U0001f381 Daily','callback_data':'daily'},{'text':'\U0001f517 Refer','callback_data':'refer'}]]); return
    typing(cid)
    try:
        r=requests.get(f"{AADHAR_API}?key={AADHAR_KEY}&id={aid}",timeout=15)
        res=r.json() if r.status_code==200 else None
    except: res=None
    db[uid]['points']-=1; db[uid]['searches']+=1
    pts_left=db[uid]['points']; save_db(db)
    records=parse_records(res) if res else []
    if not records:
        send(cid,"\u2501"*21+"\n  \u274c <b>NO DATA FOUND!</b> \u274c\n"+"\u2501"*21+f"\n\n\U0001faaa <b>Aadhaar:</b> <code>{aid}</code>\n\n\U0001f48e <b>Points Left:</b> {pts_left}",search_kb()); return
    send(cid,
        "\u2501"*21+"\n  \u2705 <b>DATA RETRIEVED!</b> \u2705\n"+"\u2501"*21+
        f"\n\n\U0001faaa <b>Aadhaar:</b> <code>{aid}</code>\n"
        f"\U0001f4ca <b>Records:</b> {len(records)} found\n\n"+
        format_records(records)+
        "\n\u2504"*19+"\n\U0001f48e <b>Points Left:</b> "+str(pts_left)+"\n\U0001f916 <b>Made by PRINCE</b>\n"+"\u2501"*21,
        search_kb())

def handle_callback(cb):
    cid=cb['message']['chat']['id']; uid=str(cb['from']['id'])
    name=cb['from'].get('first_name','User'); cbd=cb['data']
    tg('answerCallbackQuery',{'callback_query_id':cb['id']})
    db=load_db(); get_user(db,uid,name); db[uid]['name']=name

    if cbd=='check_join':
        db[uid]['joined']=True; save_db(db)
        send(cid,f"\u2501"*21+f"\n  \U0001f38a <b>WELCOME, {name}!</b> \U0001f38a\n"+"\u2501"*21+"\n\n\U0001f513 <b>Access Granted!</b>\n\U0001f48e <b>5 Free Points</b> added!\n\nChoose a tool below! \U0001f447",main_kb())
    elif cbd=='num_search':
        db[uid]['awaiting']='num'; save_db(db)
        send(cid,"\u2501"*21+"\n  \U0001f4f1 <b>NUMBER LOOKUP</b>\n"+"\u2501"*21+"\n\n\U0001f4f2 Send a <b>mobile number</b>:\n<i>Example: <code>6205923286</code></i>\n\n\U0001f48e Cost: <b>1 Point</b>",[[{'text':'\u274c Cancel','callback_data':'menu'}]])
    elif cbd=='aadhar_search':
        db[uid]['awaiting']='aadhar'; save_db(db)
        send(cid,"\u2501"*21+"\n  \U0001faaa <b>AADHAAR LOOKUP</b>\n"+"\u2501"*21+"\n\n\U0001f4f2 Send <b>12-digit Aadhaar</b>:\n<i>Example: <code>327567544017</code></i>\n\n\U0001f48e Cost: <b>1 Point</b>",[[{'text':'\u274c Cancel','callback_data':'menu'}]])
    elif cbd=='daily':
        today=str(date.today())
        if db[uid]['last_daily']==today:
            send(cid,"\U0001f381 <b>Already claimed today!</b>\n\U0001f48e Balance: <b>"+str(db[uid]['points'])+" pts</b>\n\U0001f550 Come back tomorrow!",menu_kb())
        else:
            db[uid]['points']+=2; db[uid]['last_daily']=today; save_db(db)
            send(cid,"\u2728 <b>BONUS CLAIMED!</b>\n\n\U0001f7e2 <b>+2 Points</b> added!\n\U0001f48e Balance: <b>"+str(db[uid]['points'])+" pts</b>",menu_kb())
    elif cbd=='profile':
        u=db[uid]; pts=u['points']; refs=len(u.get('referrals',[]))
        rank=('\U0001f480 LEGEND' if pts>=500 else '\U0001f451 VIP' if pts>=100 else '\U0001f947 Gold' if pts>=50 else '\U0001f948 Silver' if pts>=20 else '\U0001f949 Bronze')
        send(cid,"\u2501"*21+"\n     \U0001f464 <b>MY PROFILE</b>\n"+"\u2501"*21+f"\n\n\U0001f194 <b>ID:</b> <code>{uid}</code>\n\U0001f44b <b>Name:</b> {u['name']}\n\U0001f3c5 <b>Rank:</b> {rank}\n\U0001f48e <b>Balance:</b> {pts} pts\n\U0001f50e <b>Searches:</b> {u['searches']}\n\U0001f465 <b>Referrals:</b> {refs}",menu_kb())
    elif cbd=='refer':
        r=tg('getMe',{}); bun=r.get('result',{}).get('username','HitmanOsintBot')
        link=f"https://t.me/{bun}?start=ref_{uid}"
        send(cid,"\U0001f4b0 <b>REFER & EARN</b>\n\n\U0001f381 Each referral = <b>+5 Points</b>\n\n\U0001f4f2 <b>Your Link:</b>\n<code>"+link+"</code>\n\n\U0001f48e Balance: <b>"+str(db[uid]['points'])+" pts</b>",menu_kb())
    elif cbd=='redeem':
        db[uid]['awaiting']='promo'; save_db(db)
        send(cid,"\U0001f4b3 <b>REDEEM PROMO CODE</b>\n\n\u270d\ufe0f Send your promo code:\n<i>Example: PRINCE50</i>",[[{'text':'\u274c Cancel','callback_data':'menu'}]])
    elif cbd=='botstats':
        db2=load_db(); total=len(db2); ts=sum(u.get('searches',0) for u in db2.values())
        send(cid,f"\U0001f4ca <b>BOT STATS</b>\n\n\U0001f465 Users: <b>{total}</b>\n\U0001f50e Searches: <b>{ts}</b>",menu_kb())
    elif cbd=='menu':
        db[uid]['awaiting']=None; save_db(db)
        send(cid,welcome_msg(name,db[uid]['points']),main_kb())
    save_db(db)

def handle_message(msg):
    cid=msg['chat']['id']; uid=str(msg['from']['id'])
    name=msg['from'].get('first_name','User'); text=msg.get('text','').strip()
    db=load_db(); get_user(db,uid,name); db[uid]['name']=name

    if text.startswith('/start'):
        parts=text.split()
        if len(parts)>1 and parts[1].startswith('ref_'):
            ref_by=parts[1].replace('ref_','')
            if ref_by!=uid and not db[uid].get('referred_by'):
                db[uid]['referred_by']=ref_by; get_user(db,ref_by)
                if uid not in db[ref_by].get('referrals',[]):
                    db[ref_by]['referrals'].append(uid); db[ref_by]['points']+=5
                    tg('sendMessage',{'chat_id':ref_by,'text':f"\U0001f517 <b>NEW REFERRAL!</b>\n\U0001f464 <b>{name}</b> joined!\n\U0001f7e2 <b>+5 Points</b>!\n\U0001f48e Balance: <b>{db[ref_by]['points']} pts</b>",'parse_mode':'HTML'})
        save_db(db)
        if db[uid].get('joined'): send(cid,welcome_msg(name,db[uid]['points']),main_kb()); return
        send(cid,not_joined_msg(),[[{'text':'\U0001f4e2 Join Channel','url':CHANNEL_URL},{'text':'\u2705 Joined! Check','callback_data':'check_join'}]])
        save_db(db); return

    if not db[uid].get('joined'):
        send(cid,not_joined_msg(),[[{'text':'\U0001f4e2 Join Channel','url':CHANNEL_URL},{'text':'\u2705 Joined! Check','callback_data':'check_join'}]])
        save_db(db); return

    aw=db[uid].get('awaiting')

    if aw=='promo':
        db[uid]['awaiting']=None; codes=load_codes(); code=text.upper().strip()
        if code in codes:
            used=codes[code].get('used',[])
            if uid in used: send(cid,"\u26a0\ufe0f <b>Already used!</b>",menu_kb())
            else:
                pts=int(codes[code]['points']); db[uid]['points']+=pts
                codes[code]['used'].append(uid); save_codes(codes)
                send(cid,f"\U0001f38a <b>CODE REDEEMED!</b>\n\U0001f7e2 <b>+{pts} Points</b>!\n\U0001f48e Balance: <b>{db[uid]['points']} pts</b>",menu_kb())
        else: send(cid,"\U0001f6ab <b>Invalid code!</b>",menu_kb())
        save_db(db); return

    if aw=='num':
        db[uid]['awaiting']=None; save_db(db)
        num=text.replace('+','').replace(' ','').replace('-','')
        if not num.isdigit() or len(num)<10:
            send(cid,"\u2757 Send a valid number!\n<i>Example: <code>6205923286</code></i>",[[{'text':'\U0001f504 Try Again','callback_data':'num_search'},{'text':'\U0001f3e0 Menu','callback_data':'menu'}]]); return
        do_num_search(cid,uid,text,db); return

    if aw=='aadhar':
        db[uid]['awaiting']=None; save_db(db)
        aid=text.replace(' ','').replace('-','')
        if not aid.isdigit() or len(aid)!=12:
            send(cid,"\u2757 Send a valid 12-digit Aadhaar!\n<i>Example: <code>327567544017</code></i>",[[{'text':'\U0001f504 Try Again','callback_data':'aadhar_search'},{'text':'\U0001f3e0 Menu','callback_data':'menu'}]]); return
        do_aadhar_search(cid,uid,aid,db); return

    if uid==ADMIN_ID:
        if text.startswith('/addcode '):
            p=text.split()
            if len(p)==3:
                codes=load_codes(); codes[p[1].upper()]={'points':int(p[2]),'used':[]}; save_codes(codes)
                send(cid,f"\u2705 Code <code>{p[1].upper()}</code> \u2192 \U0001f48e <b>{p[2]} pts</b>")
            save_db(db); return
        if text.startswith('/delcode '):
            c=text.split()[1].upper(); codes=load_codes()
            if c in codes: del codes[c]; save_codes(codes); send(cid,f"\U0001f5d1\ufe0f <code>{c}</code> deleted!")
            else: send(cid,"\u274c Not found!")
            save_db(db); return
        if text.startswith('/addpoints '):
            p=text.split()
            if len(p)==3:
                get_user(db,p[1]); db[p[1]]['points']+=int(p[2]); save_db(db)
                send(cid,f"\u2705 Added \U0001f48e <b>{p[2]} pts</b> to <code>{p[1]}</code>!")
            return
        if text=='/stats':
            ts=sum(u.get('searches',0) for u in db.values())
            send(cid,f"\U0001f4ca <b>STATS</b>\n\U0001f465 Users: <b>{len(db)}</b>\n\U0001f50e Searches: <b>{ts}</b>")
            save_db(db); return
        if text.startswith('/broadcast '):
            bmsg=text[11:]; sent=0
            for bid in list(db.keys()):
                try:
                    if tg('sendMessage',{'chat_id':bid,'text':f"\U0001f4e3 <b>ANNOUNCEMENT</b>\n\n{bmsg}\n\n\U0001f916 <b>Made by PRINCE</b>",'parse_mode':'HTML'}).get('ok'): sent+=1
                except: pass
            send(cid,f"\U0001f4e2 Sent to <b>{sent}</b> users!"); save_db(db); return
        if text=='/listcodes':
            codes=load_codes()
            if not codes: send(cid,"\u274c No codes.")
            else:
                lines="\U0001f39f\ufe0f <b>Active Codes:</b>\n\n"
                for c,info in codes.items(): lines+=f"\u2523 <code>{c}</code> \u2014 \U0001f48e {info['points']} pts | Used: {len(info.get('used',[]))}x\n"
                send(cid,lines)
            save_db(db); return

    send(cid,welcome_msg(name,db[uid]['points']),main_kb())
    save_db(db)

@app.route(f'/{BOT_TOKEN}',methods=['POST'])
def webhook():
    data=request.get_json()
    if not data: return 'ok'
    if 'callback_query' in data: handle_callback(data['callback_query'])
    elif 'message' in data: handle_message(data['message'])
    return 'ok'

@app.route('/')
def index(): return '\U0001f480 HITMAN OSINT BOT \u2014 Made by PRINCE '

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',8080)))
