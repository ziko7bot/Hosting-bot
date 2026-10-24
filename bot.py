#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════
# ✦  A R C E N   H O S T I N G   U L T I M A T E   v8 ✦
# 🛡️ Anti-Crash · CPU Limiter · Smart Cleaner · High Load
# ══════════════════════════════════════════════════════════════

import ast, html, json, os, re, sys, time, uuid, shutil, subprocess
import threading, glob as _glob, base64, hashlib, platform
from datetime import datetime, timedelta
import telebot
from telebot import types

try:
    import psutil
except ImportError:
    psutil = None

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Random import get_random_bytes
    HAS_AES = True
except ImportError:
    HAS_AES = False
    print("⚠️ pycryptodome غير مثبت")

# 🛡️ حماية من الانهيار بسبب الاستدعاء الذاتي
sys.setrecursionlimit(10000)

# ══════════════════════════════════════════════════════════════
BOT_TOKEN = "8821606953:AAErLJ-5affeWcphxjymGK9sp7GHb8AsrNA"
OWNER_ID = 8746978949
ADMINS = {8746978949}
BOT_USERNAME = None

DB_FILE = "bot_database.json"
UPLOADS_DIR = "uploads"
LOGS_DIR = "logs"
PENDING_DIR = "pending"
ENCRYPTED_DIR = "encrypted"
SECURITY_FILE = "security.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_PATH = os.path.join(BASE_DIR, UPLOADS_DIR)
LOGS_PATH = os.path.join(BASE_DIR, LOGS_DIR)
PENDING_PATH = os.path.join(BASE_DIR, PENDING_DIR)
ENCRYPTED_PATH = os.path.join(BASE_DIR, ENCRYPTED_DIR)

for d in (UPLOADS_PATH, LOGS_PATH, PENDING_PATH, ENCRYPTED_PATH):
    os.makedirs(d, exist_ok=True)

IS_WINDOWS = platform.system() == "Windows"
IS_ANDROID = "ANDROID_ROOT" in os.environ

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
PER_PAGE = 6
LOG_CLEAN_INTERVAL = 1800
MAX_CPU_PERCENT = 85.0  # 🛡️ إذا وصل المعالج لهذه النسبة يرفض تشغيل بوتات جديدة

# ══════════════════════════════════════════════════════════════
PIP_NAME_MAP = {
    "telebot": "pyTelegramBotAPI", "telegram": "python-telegram-bot",
    "telethon": "telethon", "aiogram": "aiogram", "pyrogram": "pyrogram",
    "tgcrypto": "tgcrypto", "requests": "requests", "aiohttp": "aiohttp",
    "httpx": "httpx", "bs4": "beautifulsoup4", "lxml": "lxml",
    "PIL": "Pillow", "psutil": "psutil", "dotenv": "python-dotenv",
    "colorama": "colorama", "rich": "rich", "flask": "flask",
    "fastapi": "fastapi", "uvicorn": "uvicorn", "sqlalchemy": "sqlalchemy",
    "pymongo": "pymongo", "redis": "redis", "apscheduler": "apscheduler",
    "pytz": "pytz", "emoji": "emoji", "qrcode": "qrcode",
    "yt_dlp": "yt-dlp", "gtts": "gTTS", "pydub": "pydub",
    "cv2": "opencv-python-headless", "numpy": "numpy", "pandas": "pandas",
    "dateutil": "python-dateutil", "cfonts": "python-cfonts",
    "fake_useragent": "fake-useragent", "cloudscraper": "cloudscraper",
    "curl_cffi": "curl_cffi", "Crypto": "pycryptodome",
    "cryptography": "cryptography", "pyaes": "pyaes", "rsa": "rsa",
    "motor": "motor", "instagrapi": "instagrapi",
    "instaloader": "instaloader", "googletrans": "googletrans==4.0.0rc1",
    "deep_translator": "deep-translator", "mysql": "mysql-connector-python",
    "psycopg2": "psycopg2-binary", "paramiko": "paramiko",
    "boto3": "boto3", "selenium": "selenium", "playwright": "playwright",
    "dns": "dnspython", "whois": "python-whois", "feedparser": "feedparser",
    "pytube": "pytube", "moviepy": "moviepy",
    "speedtest": "speedtest-cli", "wikipedia": "wikipedia",
}

_STDLIB = set(sys.builtin_module_names) | {
    "os","sys","re","json","time","datetime","random","math","io","collections",
    "functools","itertools","threading","subprocess","shutil","glob","hashlib",
    "hmac","base64","uuid","socket","ssl","urllib","http","email","html","xml",
    "csv","sqlite3","logging","warnings","traceback","typing","asyncio",
    "concurrent","multiprocessing","queue","weakref","gc","copy","pickle",
    "struct","zlib","gzip","bz2","lzma","tarfile","zipfile","pathlib","tempfile",
    "atexit","signal","locale","gettext","argparse","configparser","secrets",
    "platform","getpass","contextlib","abc","enum","dataclasses","inspect",
    "importlib","pkgutil","site","sysconfig","builtins","future","ast",
}

def get_missing_imports(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            tree = ast.parse(f.read())
    except Exception:
        return []
    top = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names: top.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                top.add(node.module.split(".")[0])
    missing = []
    for m in top:
        if m in _STDLIB: continue
        try: 
            __import__(m) # ✅ تم إصلاح الخطأ البرمجي هنا
            continue
        except Exception: pass
        pn = PIP_NAME_MAP.get(m)
        if pn: missing.append(pn)
    return list(set(missing))

def install_for_bot(file_path):
    pkgs = get_missing_imports(file_path)
    if not pkgs: return True
    local_dir = os.path.join(BASE_DIR, ".local")
    os.makedirs(local_dir, exist_ok=True)
    for p in _glob.glob(os.path.join(local_dir, "lib/python*/site-packages")):
        if p not in sys.path: sys.path.insert(0, p)
    print(f"📦 تثبيت: {', '.join(pkgs)}", flush=True)
    cmd = [sys.executable, "-m", "pip", "install", "-U",
           "--prefix", local_dir, "--no-cache-dir", "--prefer-binary"] + pkgs
    try:
        subprocess.check_call(cmd); return True
    except Exception as e:
        print(f"⚠️ فشل: {e}"); return False

# ══════════════════════════════════════════════════════════════
_security_lock = threading.Lock()

def load_security():
    if os.path.exists(SECURITY_FILE):
        try:
            with open(SECURITY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def save_security(data):
    with _security_lock:
        with open(SECURITY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def init_security():
    if not HAS_AES: return
    sec = load_security()
    if "master_key" not in sec:
        sec["master_key"] = base64.b64encode(get_random_bytes(32)).decode()
        sec["file_keys"] = {}
        save_security(sec)

def get_master_key():
    sec = load_security()
    mk = sec.get("master_key")
    if not mk:
        mk = base64.b64encode(get_random_bytes(32)).decode()
        sec["master_key"] = mk
        save_security(sec)
    return base64.b64decode(mk)

def generate_file_key(fid, owner_id):
    if not HAS_AES: return None
    sec = load_security()
    fk = sec.setdefault("file_keys", {})
    if fid not in fk:
        combined = f"{fid}:{owner_id}:{OWNER_ID}:{BOT_TOKEN}"
        salt = hashlib.sha256(combined.encode()).digest()[:16]
        mk = get_master_key()
        kdf = hashlib.pbkdf2_hmac("sha256", mk, salt, 100000, dklen=32)
        fk[fid] = {"key": base64.b64encode(kdf).decode(),
                   "salt": base64.b64encode(salt).decode(),
                   "owner": str(owner_id)}
        sec["file_keys"] = fk
        save_security(sec)
    return fk[fid]

def get_file_key(fid):
    sec = load_security()
    return sec.get("file_keys", {}).get(fid)

def encrypt_content(content, fid, owner_id):
    if not HAS_AES: return content
    try:
        info = generate_file_key(fid, owner_id)
        key = base64.b64decode(info["key"])
        salt = base64.b64decode(info["salt"])
        cipher = AES.new(key, AES.MODE_CBC)
        ct = cipher.encrypt(pad(content.encode("utf-8"), AES.block_size))
        return json.dumps({
            "iv": base64.b64encode(cipher.iv).decode(),
            "ct": base64.b64encode(ct).decode(),
            "salt": base64.b64encode(salt).decode(),
            "fid": fid, "owner": str(owner_id),
            "ts": datetime.now().isoformat(),
        })
    except Exception as e:
        print(f"encrypt: {e}"); return None

def decrypt_content(enc_json, fid):
    if not HAS_AES: return enc_json
    try:
        data = json.loads(enc_json)
        info = get_file_key(fid)
        if not info: return None
        key = base64.b64decode(info["key"])
        iv = base64.b64decode(data["iv"])
        ct = base64.b64decode(data["ct"])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode("utf-8")
    except: return None

def save_encrypted(fid, content, owner_id):
    if not HAS_AES: return False
    enc = encrypt_content(content, fid, owner_id)
    if enc:
        path = os.path.join(ENCRYPTED_PATH, f"{fid}.enc")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(enc)
            return True
        except: return False
    return False

# ══════════════════════════════════════════════════════════════
db_lock = threading.Lock()

DEFAULT_WELCOME = (
    "💫 أهلاً <b>#name</b> في بوت رفع استضافة آركين\n\n"
    "━━━━━━━━━━━━━━━━━━━\n"
    "💰 رصيدك: <b>#balance</b> #symbol\n\n"
    "اختر من القائمة 👇"
)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        d.setdefault("settings", {})
        for k, v in {
            "channels": [], "auto_replies": {}, "welcome_text": DEFAULT_WELCOME,
            "welcome_media_type": None, "welcome_media_id": None,
            "maintenance": False, "currency_name": "نقطة",
            "currency_symbol": "💰", "upload_price": 0, "referral_reward": 0,
        }.items():
            d["settings"].setdefault(k, v)
        d.setdefault("admins", [])
        for uid_, u_ in d.get("users", {}).items():
            u_.setdefault("balance", 0)
            u_.setdefault("is_vip", False)
            u_.setdefault("vip_until", None)
        return d
    return {
        "users": {}, "files": {}, "admins": [],
        "settings": {
            "channels": [], "welcome_text": DEFAULT_WELCOME,
            "welcome_media_type": None, "welcome_media_id": None,
            "auto_replies": {}, "maintenance": False,
            "currency_name": "نقطة", "currency_symbol": "💰",
            "upload_price": 0, "referral_reward": 0,
        }
    }

def save_db():
    with db_lock:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

db = load_db()
pending_action = {}
running_processes = {}
admin_files_state = {}
user_files_state = {}
admin_member_state = {}

# ══════════════════════════════════════════════════════════════
def now_iso(): return datetime.now().isoformat()
def short_id(): return uuid.uuid4().hex[:8]
def is_admin(uid): return int(uid) in ADMINS
def is_owner(uid): return int(uid) == OWNER_ID

def sanitize_name(name):
    s = re.sub(r'[^\w\u0600-\u06FF-.]', '', name)[:40]
    return s if s else "bot"

def get_unique_folder_name(user_id, base_name):
    safe = sanitize_name(base_name)
    uu = os.path.join(UPLOADS_PATH, str(user_id))
    up = os.path.join(PENDING_PATH, str(user_id))
    counter = 0
    while True:
        cand = safe if counter == 0 else f"{safe}_{counter}"
        if not os.path.exists(os.path.join(uu, cand)) and \
           not os.path.exists(os.path.join(up, cand)) and \
           not any(f.get("folder") == cand and f.get("owner") == str(user_id)
                   for f in db["files"].values()):
            return cand
        counter += 1

def ensure_user(uid, username=None, first_name=None, last_name=None):
    k = str(uid)
    if k not in db["users"]:
        db["users"][k] = {
            "username": username or "", "first_name": first_name or "",
            "last_name": last_name or "", "points": 0, "balance": 0,
            "joined": now_iso(), "banned": False, "referrer": None,
            "is_vip": False, "vip_until": None,
        }
        save_db()
    else:
        u = db["users"][k]
        u.setdefault("balance", 0)
        u.setdefault("is_vip", False)
        u.setdefault("vip_until", None)
        if username: u["username"] = username
        if first_name: u["first_name"] = first_name
        if last_name: u["last_name"] = last_name
    return db["users"][k]

def is_vip(uid):
    if is_owner(uid) or is_admin(uid): return True
    u = db["users"].get(str(uid), {})
    if u.get("is_vip") and not u.get("vip_until"): return True
    vu = u.get("vip_until")
    if vu:
        try:
            if datetime.fromisoformat(vu) > datetime.now(): return True
        except: pass
    return False

def check_force_sub(uid):
    chs = db["settings"]["channels"]
    if not chs: return True, []
    missing = []
    for ch in chs:
        try:
            m = bot.get_chat_member(ch, uid)
            if m.status in ("left", "kicked"): missing.append(ch)
        except Exception: missing.append(ch)
    return len(missing) == 0, missing

def owner_label(owner_id):
    u = db["users"].get(str(owner_id), {})
    if u.get("username"): return f"@{u['username']}"
    if u.get("first_name"): return u["first_name"][:15]
    return str(owner_id)

def cur_name(): return db["settings"].get("currency_name", "نقطة")
def cur_sym(): return db["settings"].get("currency_symbol", "💰")
def fmt_money(a): return f"{a} {cur_sym()}"

def extract_token_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        matches = re.findall(r'\d{8,12}:[A-Za-z0-9_-]{30,50}', content)
        for m in matches:
            if re.match(r'^\d+:', m): return m
        return None
    except: return None

def extract_admin_id_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        patterns = [
            r'(?:OWNER_ID|ADMIN_ID|ADMINS?|OWNER|MASTER_ID)\s*=\s*\(?(\d{7,12})\)?',
            r'(?:OWNER_ID|ADMIN_ID|ADMINS?|OWNER|MASTER_ID)\s*=\s*\{?(\d{7,12})\}?',
        ]
        for pat in patterns:
            m = re.search(pat, content)
            if m: return m.group(1)
        return None
    except: return None

def get_bot_info_from_token(token):
    try:
        tmp = telebot.TeleBot(token, parse_mode="HTML")
        me = tmp.get_me()
        return {"username": me.username, "first_name": me.first_name, "id": me.id}
    except: return None

def human_size(b):
    if b < 1024: return f"{b} B"
    if b < 1024**2: return f"{b/1024:.1f} KB"
    if b < 1024**3: return f"{b/(1024**2):.2f} MB"
    return f"{b/(1024**3):.2f} GB"

def auto_fix_errors(code):
    fixes = [
        (r'\braw_input\b', 'input'),
        (r'\bxrange\b', 'range'),
        (r'\.iteritems\(\)', '.items()'),
        (r'\.itervalues\(\)', '.values()'),
        (r'\.iterkeys\(\)', '.keys()'),
    ]
    for pat, rep in fixes:
        try: code = re.sub(pat, rep, code)
        except: pass
    return code

def update_token_in_content(content, new_token):
    keywords = ["TOKEN", "BOT_TOKEN", "bot_token", "api_key", "API_TOKEN",
                "BOT_TKN", "TKN", "telegram_token"]
    pattern = r"(['\"])\d{8,12}:[A-Za-z0-9_-]{30,50}(['\"])"
    content = re.sub(pattern, r"\g<1>" + new_token + r"\g<2>", content)
    for kw in keywords:
        kw_pat = rf"({kw}\s*=\s*)(['\"])([^'\"]+)(['\"])"
        content = re.sub(kw_pat, r"\g<1>\g<2>" + new_token + r"\g<4>", content)
    return content

def update_admin_id_in_content(content, new_id):
    keywords = ["OWNER_ID", "ADMIN_ID", "MASTER_ID"]
    content_updated = content
    for kw in keywords:
        pat = rf"({kw}\s*=\s*)\d{{7,12}}"
        content_updated = re.sub(pat, r"\g<1>" + new_id, content_updated)
        pat_list = rf"({kw}\s*=\s*\()\d{{7,12}}(\))"
        content_updated = re.sub(pat_list, r"\g<1>" + new_id + r"\g<2>", content_updated)
        pat_set = rf"({kw}\s*=\s*\{{\s*)\d{{7,12}}(\s*\}})"
        content_updated = re.sub(pat_set, r"\g<1>" + new_id + r"\g<2>", content_updated)
    return content_updated

# ══════════════════════════════════════════════════════════════
# ✨ دوال التنظيف الذكي (AI Cleanup)
# ══════════════════════════════════════════════════════════════

def get_dir_size(path):
    total = 0
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try: total += os.path.getsize(fp)
                except: pass
    except: pass
    return total

def ai_scan_system():
    report = {
        "logs_size": 0, "logs_count": 0, "logs_to_clean": [],
        "orphan_uploads": [], "orphan_encrypted": [],
        "empty_folders": [], "duplicate_files": {},
        "stale_pending": [], "stale_stopped": [], "stale_failed": [],
        "old_orphan_dirs": [], "total_recoverable": 0,
    }
    
    # 1. السجلات
    for lp in _glob.glob(os.path.join(LOGS_PATH, "*.log")):
        try:
            sz = os.path.getsize(lp)
            report["logs_size"] += sz
            report["logs_count"] += 1
            if sz > 10 * 1024:
                report["logs_to_clean"].append({"path": lp, "size": sz})
        except: pass
        
    # 2. ملفات مرفوعة بدون مرجع في DB (orphan)
    files_in_db = set()
    for fid, f in db["files"].items():
        if f.get("folder") and f.get("owner"):
            files_in_db.add((str(f["owner"]), f["folder"]))
            
    for user_dir in _glob.glob(os.path.join(UPLOADS_PATH, "*")):
        if not os.path.isdir(user_dir): continue
        user_id = os.path.basename(user_dir)
        for folder in _glob.glob(os.path.join(user_dir, "*")):
            if not os.path.isdir(folder): continue
            folder_name = os.path.basename(folder)
            if (user_id, folder_name) not in files_in_db:
                sz = get_dir_size(folder)
                report["orphan_uploads"].append({
                    "path": folder, "user": user_id,
                    "folder": folder_name, "size": sz
                })
                report["total_recoverable"] += sz
                
    # 3. ملفات مشفرة بدون مرجع
    enc_in_db = set(fid for fid in db["files"].keys())
    for ep in _glob.glob(os.path.join(ENCRYPTED_PATH, "*.enc")):
        fid = os.path.basename(ep).replace(".enc", "")
        if fid not in enc_in_db:
            sz = os.path.getsize(ep)
            report["orphan_encrypted"].append({"path": ep, "fid": fid, "size": sz})
            report["total_recoverable"] += sz
            
    # 4. مجلدات فارغة
    for user_dir in _glob.glob(os.path.join(UPLOADS_PATH, "*")):
        if not os.path.isdir(user_dir): continue
        try:
            if not os.listdir(user_dir):
                report["empty_folders"].append({"path": user_dir, "type": "uploads"})
        except: pass
        
    for user_dir in _glob.glob(os.path.join(PENDING_PATH, "*")):
        if not os.path.isdir(user_dir): continue
        try:
            for folder in _glob.glob(os.path.join(user_dir, "*")):
                if os.path.isdir(folder) and not os.listdir(folder):
                    report["empty_folders"].append({"path": folder, "type": "pending"})
            if not os.listdir(user_dir):
                report["empty_folders"].append({"path": user_dir, "type": "pending_user"})
        except: pass
        
    # 5. ملفات مكررة (نفس الاسم لنفس المستخدم)
    seen = {}
    for fid, f in db["files"].items():
        key = (str(f.get("owner")), f.get("filename"))
        if key in seen:
            report["duplicate_files"].setdefault(key, []).append(fid)
        else:
            seen[key] = fid
            
    # 6. معلقة قديمة (> 24 ساعة)
    now = time.time()
    for fid, f in db["files"].items():
        try:
            uploaded = datetime.fromisoformat(f.get("uploaded_at", "")).timestamp()
            age_hours = (now - uploaded) / 3600
            if f.get("status") == "pending" and age_hours > 24:
                report["stale_pending"].append({"fid": fid, "name": f.get("filename"), "age_h": age_hours})
            elif f.get("status") == "stopped" and age_hours > 7 * 24:
                report["stale_stopped"].append({"fid": fid, "name": f.get("filename"), "age_d": age_hours / 24})
            elif f.get("status") == "failed" and age_hours > 3 * 24:
                report["stale_failed"].append({"fid": fid, "name": f.get("filename"), "age_d": age_hours / 24})
        except: pass
        
    # 7. مجلدات .local كبيرة جداً (cache من pip)
    local_dir = os.path.join(BASE_DIR, ".local")
    if os.path.exists(local_dir):
        sz = get_dir_size(local_dir)
        if sz > 200 * 1024 * 1024:
            report["old_orphan_dirs"].append({
                "path": local_dir, "type": "pip_cache", "size": sz
            })
            
    return report

def do_real_cleanup(action, extra=None):
    count = 0
    freed = 0
    
    if action == "logs":
        for lp in _glob.glob(os.path.join(LOGS_PATH, "*.log")):
            try:
                sz = os.path.getsize(lp)
                if sz > 10 * 1024:
                    with open(lp, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    with open(lp, "w", encoding="utf-8") as f:
                        f.writelines(lines[-200:])
                    new_sz = os.path.getsize(lp)
                    freed += (sz - new_sz)
                    count += 1
            except: pass
            
    elif action == "orphan_uploads":
        files_in_db = set()
        for fid, f in db["files"].items():
            if f.get("folder") and f.get("owner"):
                files_in_db.add((str(f["owner"]), f["folder"]))
                
        for user_dir in _glob.glob(os.path.join(UPLOADS_PATH, "*")):
            if not os.path.isdir(user_dir): continue
            user_id = os.path.basename(user_dir)
            for folder in _glob.glob(os.path.join(user_dir, "*")):
                if not os.path.isdir(folder): continue
                folder_name = os.path.basename(folder)
                if (user_id, folder_name) not in files_in_db:
                    sz = get_dir_size(folder)
                    shutil.rmtree(folder, ignore_errors=True)
                    freed += sz
                    count += 1
                    
    elif action == "orphan_encrypted":
        enc_in_db = set(fid for fid in db["files"].keys())
        for ep in _glob.glob(os.path.join(ENCRYPTED_PATH, "*.enc")):
            fid = os.path.basename(ep).replace(".enc", "")
            if fid not in enc_in_db:
                try:
                    sz = os.path.getsize(ep)
                    os.remove(ep)
                    freed += sz
                    count += 1
                except: pass
                
    elif action == "empty_folders":
        for root in (UPLOADS_PATH, PENDING_PATH):
            for dirpath in _glob.glob(os.path.join(root, "**/"), recursive=True):
                try:
                    if os.path.isdir(dirpath) and not os.listdir(dirpath):
                        os.rmdir(dirpath)
                        count += 1
                except: pass
                
    elif action == "duplicates":
        seen = {}
        now = time.time()
        for fid, f in list(db["files"].items()):
            key = (str(f.get("owner")), f.get("filename"))
            uploaded = f.get("uploaded_at", "")
            if key in seen:
                prev_fid, prev_time = seen[key]
                if uploaded > prev_time:
                    delete_file_full(prev_fid)
                    count += 1
                    seen[key] = (fid, uploaded)
                else:
                    delete_file_full(fid)
                    count += 1
            else:
                seen[key] = (fid, uploaded)
                
    elif action == "stale_pending":
        now = time.time()
        for fid, f in list(db["files"].items()):
            try:
                if f.get("status") != "pending": continue
                uploaded = datetime.fromisoformat(f.get("uploaded_at", "")).timestamp()
                if (now - uploaded) / 3600 > 24:
                    pf = f.get("pending_path")
                    if pf:
                        pd = os.path.dirname(pf)
                        if os.path.exists(pd):
                            sz = get_dir_size(pd)
                            shutil.rmtree(pd, ignore_errors=True)
                            freed += sz
                    db["files"].pop(fid, None)
                    count += 1
            except: pass
        save_db()
        
    elif action == "stale_stopped":
        now = time.time()
        for fid, f in list(db["files"].items()):
            try:
                if f.get("status") != "stopped": continue
                uploaded = datetime.fromisoformat(f.get("uploaded_at", "")).timestamp()
                if (now - uploaded) / 86400 > 7:
                    delete_file_full(fid)
                    count += 1
            except: pass
            
    elif action == "stale_failed":
        now = time.time()
        for fid, f in list(db["files"].items()):
            try:
                if f.get("status") != "failed": continue
                uploaded = datetime.fromisoformat(f.get("uploaded_at", "")).timestamp()
                if (now - uploaded) / 86400 > 3:
                    delete_file_full(fid)
                    count += 1
            except: pass
            
    elif action == "pip_cache":
        local_dir = os.path.join(BASE_DIR, ".local")
        if os.path.exists(local_dir):
            sz = get_dir_size(local_dir)
            shutil.rmtree(local_dir, ignore_errors=True)
            freed += sz
            count += 1
            
    elif action == "full":
        r = do_real_cleanup("logs")
        count += r[0]; freed += r[1]
        r = do_real_cleanup("orphan_encrypted")
        count += r[0]; freed += r[1]
        r = do_real_cleanup("stale_pending")
        count += r[0]; freed += r[1]
        r = do_real_cleanup("stale_failed")
        count += r[0]; freed += r[1]
        r = do_real_cleanup("duplicates")
        count += r[0]; freed += r[1]
        r = do_real_cleanup("empty_folders")
        count += r[0]; freed += r[1]
        r = do_real_cleanup("orphan_uploads")
        count += r[0]; freed += r[1]
        
    return count, freed

def build_ai_report():
    r = ai_scan_system()
    total_size = get_dir_size(BASE_DIR)
    uploads_size = get_dir_size(UPLOADS_PATH)
    pending_size = get_dir_size(PENDING_PATH)
    logs_size = r["logs_size"]
    enc_size = get_dir_size(ENCRYPTED_PATH)
    local_size = get_dir_size(os.path.join(BASE_DIR, ".local"))
    
    txt = (
        f"🤖 <b>تحليل ذكي للسيرفر</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>💾 المساحات:</b>\n"
        f"   📦 إجمالي المشروع: <b>{human_size(total_size)}</b>\n"
        f"   📤 ملفات المستخدمين: <b>{human_size(uploads_size)}</b>\n"
        f"   ⏳ قائمة الانتظار: <b>{human_size(pending_size)}</b>\n"
        f"   📋 السجلات: <b>{human_size(logs_size)}</b>\n"
        f"   🔐 مشفرة: <b>{human_size(enc_size)}</b>\n"
        f"   📚 مكتبات pip: <b>{human_size(local_size)}</b>\n\n"
        f"<b>🎯 قابل للاسترداد:</b> <b>{human_size(r['total_recoverable'])}</b>\n\n"
    )
    
    suggestions = []
    if r["logs_count"] > 5:
        suggestions.append(f"📋 {len(r['logs_to_clean'])} سجل كبير ({human_size(sum(l['size'] for l in r['logs_to_clean']))})")
    if r["orphan_uploads"]:
        sz = sum(o["size"] for o in r["orphan_uploads"])
        suggestions.append(f"🗑️ {len(r['orphan_uploads'])} مجلد يتيم ({human_size(sz)})")
    if r["orphan_encrypted"]:
        sz = sum(o["size"] for o in r["orphan_encrypted"])
        suggestions.append(f"🔐 {len(r['orphan_encrypted'])} ملف مشفر يتيم ({human_size(sz)})")
    if r["empty_folders"]:
        suggestions.append(f"📁 {len(r['empty_folders'])} مجلد فارغ")
    if r["duplicate_files"]:
        total_dups = sum(len(v) for v in r["duplicate_files"].values())
        suggestions.append(f"🔁 {total_dups} ملف مكرر")
    if r["stale_pending"]:
        suggestions.append(f"⏳ {len(r['stale_pending'])} معلق قديم (>24س)")
    if r["stale_stopped"]:
        suggestions.append(f"🔴 {len(r['stale_stopped'])} متوقف قديم (>7ي)")
    if r["stale_failed"]:
        suggestions.append(f"⚠️ {len(r['stale_failed'])} فاشل قديم (>3ي)")
    if r["old_orphan_dirs"]:
        suggestions.append(f"📚 pip cache كبير ({human_size(local_size)})")
        
    if suggestions:
        txt += "<b>💡 اقتراحات التنظيف:</b>\n"
        for s in suggestions:
            txt += f"   • {s}\n"
    else:
        txt += "✅ <b>السيرفر نظيف — لا حاجة لتنظيف</b>\n"
        
    return txt

def cleanup_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("🤖 تحليل ذكي", "💾 عرض المساحة")
    kb.add("⚡ تنظيف سريع", "🔥 تنظيف شامل")
    kb.add("📋 تنظيف السجلات", "📁 حذف المجلدات الفارغة")
    kb.add("🔐 تنظيف التشفير المعلق", "🗑️ حذف الملفات اليتيمة")
    kb.add("⏳ حذف المعلق القديم", "🔁 حذف المكررات")
    kb.add("🗑️ حذف المتوقفة القديمة", "⚠️ حذف الفاشلة القديمة")
    kb.add("📚 حذف pip cache")
    kb.add("🔙 لوحة الإدارة")
    return kb

# ══════════════════════════════════════════════════════════════
def main_menu_kb(uid):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📤 رفع ملف", "📁 ملفاتي")
    kb.add("👤 حسابي", "📊 إحصائياتي")
    kb.add("🎁 دعوة صديق", "📖 التعليمات")
    kb.add("💬 الدعم الفني")
    if is_admin(uid):
        kb.add("⚙️ لوحة الإدارة")
    return kb

def admin_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📁 الملفات", "👥 المستخدمين")
    kb.add("💰 الرصيد والعملة", "⚙️ الأسعار")
    kb.add("👋 الترحيب", "💬 الردود")
    kb.add("⚪ القنوات", "👑 المشرفين")
    kb.add("📊 السيرفر", "📢 إذاعة")
    kb.add("🧹 التنظيف الذكي")
    kb.add("🔙 القائمة")
    return kb

def files_admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📋 الكل", "⏳ معلّق")
    kb.add("🟢 شغال", "🔴 متوقف")
    kb.add("▶️ تشغيل الكل", "⏹ إيقاف الكل")
    kb.add("🗑️ حذف المتوقفة")
    kb.add("🔙 لوحة الإدارة")
    return kb

def users_admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("🔍 بحث عضو")
    kb.add("📋 آخر المستخدمين")
    kb.add("🔙 لوحة الإدارة")
    return kb

def cancel_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("❌ إلغاء")
    return kb

def confirm_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("✅ نعم", "❌ لا")
    return kb

def member_actions_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("➕ رصيد", "➖ رصيد")
    kb.add("💰 تصفير")
    kb.add("💎 منح VIP", "🆓 سحب VIP")
    kb.add("🚫 حظر/فك")
    kb.add("📁 ملفاته")
    kb.add("🔙 رجوع")
    return kb

def welcome_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("📝 تعديل النص", "🖼 وسائط")
    kb.add("🗑 حذف الوسائط", "👁 معاينة")
    kb.add("📖 المتغيرات", "🔄 الافتراضي")
    kb.add("🔙 لوحة الإدارة")
    return kb

def auto_replies_menu_kb(uid):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    ars = db["settings"]["auto_replies"]
    for i, k in enumerate(list(ars.keys())[:15], 1):
        kb.add(f"🗑 {i}. {k[:30]}")
    kb.add("➕ إضافة رد")
    if ars: kb.add("❌ حذف الكل")
    kb.add("🔙 لوحة الإدارة")
    return kb

def currency_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("💱 اسم العملة", "🔣 الرمز")
    kb.add("🔙 لوحة الإدارة")
    return kb

def pricing_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("📤 سعر الرفع")
    kb.add("🎁 مكافأة الإحالة")
    kb.add("🔙 لوحة الإدارة")
    return kb

def channels_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("➕ إضافة", "🗑 حذف")
    kb.add("🔙 لوحة الإدارة")
    return kb

def admins_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("➕ إضافة مشرف", "🗑 حذف مشرف")
    kb.add("🔙 لوحة الإدارة")
    return kb

# ══════════════════════════════════════════════════════════════
def user_files_menu_kb(uid):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    visible = {}
    uf = {fid: f for fid, f in db["files"].items()
          if f["owner"] == str(uid) and f.get("status") in
          ("approved", "running", "stopped", "failed")}
    for fid, f in uf.items():
        ir = is_process_running(fid)
        icon = "🟢" if ir else "🔴"
        if f.get("status") == "failed": icon = "⚠️"
        label = f"{icon} {f['filename']}"[:55]
        base = label; c = 1
        while label in visible:
            label = f"{base[:50]} ({c})"; c += 1
        visible[label] = fid
        kb.add(label)
    if not uf:
        kb.add("📭 لا توجد ملفات")
    user_files_state[uid] = {"visible": visible, "sel_fid": None}
    kb.add("🔙 القائمة")
    return kb

def user_file_control_kb(fid):
    running = is_process_running(fid)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if running:
        kb.add("⏹ إيقاف", "♻️ إعادة")
    else:
        kb.add("▶️ تشغيل", "♻️ إعادة")
    kb.add("📋 السجل", "📊 التفاصيل")
    kb.add("⌨️ التيرمنال", "📥 تحميل")
    kb.add("📝 تعديل الكود", "🔧 إصلاح")
    kb.add("🔑 تغيير التوكن", "🆔 تغيير الآيدي")
    kb.add("🗑️ حذف")
    kb.add("🔙 ملفاتي")
    return kb

def send_user_files(chat_id, uid):
    kb = user_files_menu_kb(uid)
    uf = {fid: f for fid, f in db["files"].items()
          if f["owner"] == str(uid) and f.get("status") in
          ("approved", "running", "stopped", "failed")}
    pend = [fid for fid, f in db["files"].items()
            if f["owner"] == str(uid) and f.get("status") == "pending"]
    running = sum(1 for fid in uf if is_process_running(fid))
    bot.send_message(chat_id,
        f"📁 <b>ملفاتي</b>\n"
        f"📦 {len(uf)} · 🟢 {running} · 🔴 {len(uf)-running} · ⏳ {len(pend)}",
        reply_markup=kb)

def send_user_file_control(chat_id, uid, fid):
    f = db["files"].get(fid)
    if not f or f.get("owner") != str(uid):
        bot.send_message(chat_id, "❌ غير مصرح"); return
    running = is_process_running(fid)
    st = "🟢 شغال" if running else "🔴 متوقف"
    if f.get("status") == "failed": st = "⚠️ فشل"
    p = f.get("path"); sz = 0
    if p and os.path.exists(p):
        try: sz = os.path.getsize(p)
        except: pass
    bname = f.get("bot_username")
    body = (
        f"🕹️ <b>تفاصيل ملفك</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📄 <b>الاسم:</b> <code>{html.escape(f['filename'])}</code>\n"
        f"📁 <b>المجلد:</b> <code>{html.escape(f.get('folder') or '—')}</code>\n"
        f"⚡ <b>الحالة:</b> {st}\n"
        f"📦 <b>الحجم:</b> {human_size(sz)}\n"
        f"🔢 <b>PID:</b> <code>{f.get('pid') or '—'}</code>\n"
        f"📅 <b>الرفع:</b> <code>{f.get('uploaded_at','')[:19]}</code>\n"
    )
    if bname:
        body += f"🤖 <b>البوت:</b> @{html.escape(bname)}\n"
    if f.get("hours"):
        body += f"⏰ <b>الساعات:</b> {f.get('hours')}\n"
    user_files_state.setdefault(uid, {})["sel_fid"] = fid
    bot.send_message(chat_id, body, reply_markup=user_file_control_kb(fid))

# ══════════════════════════════════════════════════════════════
def build_admin_files_kb(uid, page=0, filt=None):
    items = list(db["files"].items())
    if filt:
        items = [(fid, f) for fid, f in items if f.get("status") == filt]
    total = len(items)
    tp = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(0, min(page, tp - 1))
    start = page * PER_PAGE
    end = min(start + PER_PAGE, total)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    visible = {}
    for fid, f in items[start:end]:
        running = is_process_running(fid)
        icon = "🟢" if running else "🔴"
        if f.get("status") == "pending": icon = "⏳"
        elif f.get("status") == "failed": icon = "⚠️"
        owner = owner_label(f.get("owner"))
        bname = f.get("bot_username") or f["filename"]
        label = f"{icon} {bname} · {owner}"[:55]
        base = label; c = 1
        while label in visible:
            label = f"{base[:50]} ({c})"; c += 1
        visible[label] = fid
        kb.add(label)
    if not items:
        kb.add("📭 لا توجد ملفات")

    if tp > 1:
        row = []
        if page > 0: row.append("◀️ السابق")
        row.append(f"📄 {page+1}/{tp}")
        if end < total: row.append("▶️ التالي")
        kb.add(*row)

    kb.add("📋 الكل", "⏳ معلّق")
    kb.add("🟢 شغال", "🔴 متوقف")
    kb.add("▶️ تشغيل الكل", "⏹ إيقاف الكل")
    kb.add("🗑️ حذف المتوقفة")
    kb.add("🔙 لوحة الإدارة")

    admin_files_state[uid] = {"page": page, "filter": filt,
                              "visible": visible, "sel_fid": None}
    return kb, total, tp, page

def send_admin_files(chat_id, uid, page=0, filt=None):
    kb, total, tp, page = build_admin_files_kb(uid, page, filt)
    titles = {"pending": "⏳ المعلّقة", "running": "🟢 الشغالة",
              "stopped": "🔴 المتوقفة", "failed": "⚠️ الفاشلة"}
    title = titles.get(filt, "📁 كل الملفات")
    stats = []
    for st, ic in [("running", "🟢"), ("stopped", "🔴"),
                   ("failed", "⚠️"), ("pending", "⏳")]:
        c = sum(1 for _, f in db["files"].items() if f.get("status") == st)
        if c: stats.append(f"{ic}{c}")
    header = " · ".join(stats) if stats else "📭"
    bot.send_message(chat_id,
        f"{title} · {header}\n"
        f"📄 صفحة {page+1}/{tp} · {total} ملف",
        reply_markup=kb)

def admin_file_control_kb(fid):
    f = db["files"].get(fid, {})
    running = is_process_running(fid)
    is_pending = f.get("status") == "pending"
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if is_pending:
        kb.add("✅ قبول", "❌ رفض")
        kb.add("🔙 رجوع للقائمة")
        return kb
    if running:
        kb.add("⏹ إيقاف", "♻️ إعادة")
    else:
        kb.add("▶️ تشغيل", "♻️ إعادة")
    kb.add("📋 السجل", "📊 التفاصيل")
    kb.add("⌨️ التيرمنال", "📥 تحميل")
    kb.add("📝 تعديل", "🔧 إصلاح")
    kb.add("🔑 التوكن", "🆔 الآيدي")
    kb.add("🗑️ حذف")
    kb.add("🔙 رجوع للقائمة")
    return kb

def send_admin_file_control(chat_id, uid, fid):
    f = db["files"].get(fid)
    if not f:
        bot.send_message(chat_id, "❌ غير موجود"); return
    running = is_process_running(fid)
    is_pending = f.get("status") == "pending"
    owner_id = f.get("owner", "—")
    owner = owner_label(owner_id)
    p = f.get("path") or f.get("pending_path")
    sz = 0
    if p and os.path.exists(p):
        try: sz = os.path.getsize(p)
        except: pass
    if is_pending: st = "⏳ بانتظار الموافقة"
    elif running: st = "🟢 شغال"
    elif f.get("status") == "failed": st = "⚠️ فشل"
    else: st = "🔴 متوقف"
    token_str = "—"
    if f.get("token"):
        t = f["token"]
        token_str = t[:15] + "..." + t[-6:] if len(t) > 25 else t
    body = (
        f"🕹️ <b>تفاصيل الملف</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📄 <b>الاسم:</b> <code>{html.escape(f['filename'])}</code>\n"
        f"👤 <b>المالك:</b> {html.escape(owner)}\n"
        f"🆔 <b>الآيدي:</b> <code>{owner_id}</code>\n"
        f"📁 <b>المجلد:</b> <code>{html.escape(f.get('folder') or '—')}</code>\n"
        f"⚡ <b>الحالة:</b> {st}\n"
        f"📦 <b>الحجم:</b> {human_size(sz)}\n"
        f"🔢 <b>PID:</b> <code>{f.get('pid') or '—'}</code>\n"
        f"📅 <b>الرفع:</b> <code>{f.get('uploaded_at','')[:19]}</code>\n"
    )
    if f.get("bot_username"):
        body += f"🤖 <b>البوت:</b> @{html.escape(f['bot_username'])}\n"
    if f.get("bot_name"):
        body += f"📛 <b>اسم البوت:</b> {html.escape(f['bot_name'])}\n"
    if f.get("bot_id"):
        body += f"🆔 <b>ID البوت:</b> <code>{f.get('bot_id')}</code>\n"
    body += f"🔑 <b>التوكن:</b> <code>{token_str}</code>\n"
    if f.get("hours"):
        body += f"⏰ <b>الساعات:</b> {f.get('hours')}\n"
    if p:
        body += f"\n📍 <b>المسار:</b>\n<code>{html.escape(p)}</code>\n"
    admin_files_state.setdefault(uid, {})["sel_fid"] = fid
    bot.send_message(chat_id, body, reply_markup=admin_file_control_kb(fid))

# ══════════════════════════════════════════════════════════════
def is_process_running(fid):
    proc = running_processes.get(fid)
    if proc and proc.poll() is None: return True
    f = db["files"].get(fid)
    if f and f.get("pid"):
        try:
            os.kill(f["pid"], 0); return True
        except (OSError, ProcessLookupError):
            f["pid"] = None
            if f["status"] == "running": f["status"] = "stopped"
            save_db()
            return False

def start_hosted_bot(fid):
    f = db["files"].get(fid)
    if not f: return False, "الملف غير موجود."
    if f.get("status") == "pending": return False, "⏳ قيد المراجعة."
    p = f.get("path")
    if not p or not os.path.exists(p): return False, "المسار غير موجود."
    if is_process_running(fid): return False, "يعمل بالفعل."
    if os.path.splitext(f["filename"])[1].lower() != ".py":
        return False, "مسموح .py فقط."

    # 🛡️ درع الحماية: فحص المعالج قبل تشغيل ملف جديد
    if psutil:
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            if cpu_usage > MAX_CPU_PERCENT:
                return False, f"⚠️ السيرفر تحت ضغط عالي ({cpu_usage}%). يرجى الانتظار."
        except: pass

    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        try: install_for_bot(p)
        except Exception as e: print(f"⚠️ {e}", flush=True)
        log_path = os.path.join(LOGS_PATH, f"{fid}.log")
        log_file = open(log_path, "a", encoding="utf-8")
        env = os.environ.copy()
        local_dir = os.path.join(BASE_DIR, ".local")
        sp = _glob.glob(os.path.join(local_dir, "lib/python*/site-packages"))
        if sp:
            prev = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = os.pathsep.join(sp + ([prev] if prev else []))
        popen_kwargs = {
            "stdout": log_file, "stderr": subprocess.STDOUT,
            "stdin": subprocess.PIPE,
            "cwd": os.path.dirname(os.path.abspath(p)), "env": env,
        }
        if not IS_WINDOWS and not IS_ANDROID:
            popen_kwargs["start_new_session"] = True
        proc = subprocess.Popen([sys.executable, "-u", p], **popen_kwargs)
        running_processes[fid] = proc
        f["status"] = "running"; f["pid"] = proc.pid; save_db()
        return True, "✅ تم التشغيل"
    except Exception as e:
        f["status"] = "failed"; save_db()
        return False, f"❌ فشل: {e}"

def stop_hosted_bot(fid):
    f = db["files"].get(fid)
    proc = running_processes.pop(fid, None)
    if proc:
        try: proc.terminate(); proc.wait(timeout=1)
        except:
            try: proc.kill()
            except: pass
    if f and f.get("pid"):
        try:
            if IS_WINDOWS: os.kill(f["pid"], 9)
            else:
                try: os.killpg(os.getpgid(f["pid"]), 9)
                except: os.kill(f["pid"], 9)
        except: pass
    if f:
        f["status"] = "stopped"; f["pid"] = None; save_db()

def delete_file_full(fid):
    f = db["files"].get(fid)
    if not f: return False
    try:
        stop_hosted_bot(fid)
        owner = f.get("owner"); folder = f.get("folder")
        if owner and folder:
            for base in (UPLOADS_PATH, PENDING_PATH):
                fp = os.path.join(base, owner, folder)
                if os.path.exists(fp): shutil.rmtree(fp, ignore_errors=True)
        lp = os.path.join(LOGS_PATH, f"{fid}.log")
        if os.path.exists(lp):
            try: os.remove(lp)
            except: pass
        ep = os.path.join(ENCRYPTED_PATH, f"{fid}.enc")
        if os.path.exists(ep):
            try: os.remove(ep)
            except: pass
        sec = load_security()
        fk = sec.get("file_keys", {})
        if fid in fk:
            del fk[fid]; sec["file_keys"] = fk; save_security(sec)
        db["files"].pop(fid, None); save_db()
        return True
    except: return False

def restart_hosted_bot(fid):
    stop_hosted_bot(fid); time.sleep(0.6)
    return start_hosted_bot(fid)

def write_proc(fid, cmd):
    if fid in running_processes:
        proc = running_processes[fid]
        if proc.poll() is None and proc.stdin:
            try:
                proc.stdin.write(cmd.encode("utf-8") + b"\n")
                proc.stdin.flush()
                return True
            except: pass
    return False

# ══════════════════════════════════════════════════════════════
def format_welcome_text(text, user_id):
    if not text: return ""
    u = db["users"].get(str(user_id), {})
    fn = u.get("first_name", "") or "المستخدم"
    ln = u.get("last_name", "") or ""
    un = u.get("username", "") or ""
    full = f"{fn} {ln}".strip()
    bU = BOT_USERNAME or "unknown"
    inv = f"https://t.me/{bU}?start={user_id}"
    name_user = f"{full} (@{un})" if un else full
    bal = u.get("balance", 0)
    return (text.replace("#name_user", html.escape(name_user))
            .replace("#username", html.escape(f"@{un}" if un else "بدون يوزر"))
            .replace("#name", html.escape(full))
            .replace("#id", str(user_id))
            .replace("#points", str(u.get("points", 0)))
            .replace("#balance", str(bal))
            .replace("#symbol", cur_sym())
            .replace("#currency", cur_name())
            .replace("#invitelink", inv)
            .replace("#bot_username", bU))

def format_reply_text(text, user_id):
    if not text: return ""
    u = db["users"].get(str(user_id), {})
    full = f"{u.get('first_name','') or ''} {u.get('last_name','') or ''}".strip()
    un = u.get("username", "") or ""
    return (text.replace("#id", str(user_id))
            .replace("#name", html.escape(full))
            .replace("#username", f"@{un}" if un else "بدون يوزر"))

# ══════════════════════════════════════════════════════════════
@bot.message_handler(commands=["start"])
def cmd_start(message):
    uid = message.from_user.id
    u = ensure_user(uid, message.from_user.username,
                    message.from_user.first_name, message.from_user.last_name)
    if u.get("banned"):
        bot.send_message(message.chat.id, "🚫 حسابك محظور."); return
    if db["settings"].get("maintenance") and not is_admin(uid):
        bot.send_message(message.chat.id, "🔧 البوت تحت الصيانة."); return

    pending_action.pop(uid, None)
    user_files_state.pop(uid, None)
    admin_files_state.pop(uid, None)
    admin_member_state.pop(uid, None)

    parts = message.text.split()
    if len(parts) > 1 and parts[1].isdigit():
        ref = parts[1]
        if ref != str(uid) and not u.get("referrer"):
            u["referrer"] = ref
            db["users"][str(uid)]["referrer"] = ref
            reward = int(db["settings"].get("referral_reward", 0))
            if ref in db["users"] and reward > 0:
                db["users"][ref]["balance"] = db["users"][ref].get("balance", 0) + reward
                try:
                    bot.send_message(int(ref),
                        f"🎁 <b>مكافأة إحالة!</b>\n💰 +{fmt_money(reward)}")
                except: pass
            save_db()

    ok, missing = check_force_sub(uid)
    if not ok:
        kb = types.InlineKeyboardMarkup()
        for ch in missing:
            kb.add(types.InlineKeyboardButton(f"📢 {ch}",
                   url=f"https://t.me/{ch.lstrip('@')}"))
        bot.send_message(message.chat.id, "⚠️ اشترك أولاً:", reply_markup=kb); return

    wt = format_welcome_text(db["settings"]["welcome_text"], uid)
    mt = db["settings"]["welcome_media_type"]
    mi = db["settings"]["welcome_media_id"]
    try:
        if mt and mi:
            if mt == "photo": bot.send_photo(message.chat.id, mi, caption=wt, reply_markup=main_menu_kb(uid))
            elif mt == "video": bot.send_video(message.chat.id, mi, caption=wt, reply_markup=main_menu_kb(uid))
            elif mt == "animation": bot.send_animation(message.chat.id, mi, caption=wt, reply_markup=main_menu_kb(uid))
            else: bot.send_message(message.chat.id, wt, reply_markup=main_menu_kb(uid))
        else:
            bot.send_message(message.chat.id, wt, reply_markup=main_menu_kb(uid))
    except Exception:
        bot.send_message(message.chat.id, "👋 أهلاً!", reply_markup=main_menu_kb(uid))

@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if not is_admin(message.from_user.id): return
    bot.send_message(message.chat.id, "🛡️ لوحة الإدارة:", reply_markup=admin_menu_kb())

@bot.message_handler(commands=["id"])
def cmd_id(message):
    bot.reply_to(message, f"🆔 <code>{message.from_user.id}</code>")

# ══════════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: call.data.startswith("pend_"))
def handle_pending_action(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "غير مصرح"); return

    parts = call.data.split("_", 2)
    action = parts[1]
    fid = parts[2]

    f = db["files"].get(fid)
    if not f or f.get("status") != "pending":
        bot.answer_callback_query(call.id, "الملف لم يعد معلقاً", show_alert=True)
        try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except: pass
        return

    owner = f["owner"]
    folder = f.get("folder")

    if action == "accept":
        try:
            pf = f.get("pending_path")
            uu = os.path.join(UPLOADS_PATH, owner)
            bf = os.path.join(uu, folder)
            os.makedirs(bf, exist_ok=True)
            final_path = os.path.join(bf, f["filename"])
            if pf and os.path.exists(pf):
                with open(pf, "rb") as fp: content = fp.read()
                with open(final_path, "wb") as fp: fp.write(content)
                if HAS_AES:
                    try: save_encrypted(fid, content.decode("utf-8", errors="ignore"), owner)
                    except: pass
                try:
                    pd = os.path.dirname(pf)
                    if os.path.exists(pd) and not os.listdir(pd): os.rmdir(pd)
                    pu = os.path.dirname(pd)
                    if os.path.exists(pu) and not os.listdir(pu): os.rmdir(pu)
                except: pass
            f["folder"] = folder; f["path"] = final_path
            f["status"] = "approved"; f.pop("pending_path", None)
            save_db()
            ok, m = start_hosted_bot(fid)
            bot.answer_callback_query(call.id, "✅ تم القبول")
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except: pass
            bot.send_message(call.message.chat.id,
                f"✅ تم قبول <code>{html.escape(f['filename'])}</code>\n{m}")
            try:
                bot.send_message(int(owner),
                    f"🎉 <b>تم قبول ملفك!</b>\n📄 <code>{html.escape(f['filename'])}</code>",
                    reply_markup=main_menu_kb(int(owner)))
            except: pass
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ {e}", show_alert=True)

    elif action == "reject":
        try:
            pf = f.get("pending_path")
            if pf:
                pd = os.path.dirname(pf)
                if os.path.exists(pd): shutil.rmtree(pd, ignore_errors=True)
            db["files"].pop(fid, None); save_db()
            bot.answer_callback_query(call.id, "❌ تم الرفض")
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except: pass
            bot.send_message(call.message.chat.id,
                f"❌ تم رفض <code>{html.escape(f['filename'])}</code>")
            try:
                bot.send_message(int(owner),
                    f"❌ <b>تم رفض ملفك</b>\n📄 <code>{html.escape(f['filename'])}</code>",
                    reply_markup=main_menu_kb(int(owner)))
            except: pass
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ {e}", show_alert=True)

    elif action == "leave":
        bot.answer_callback_query(call.id, "⏭️ تم الترك — الملف باقٍ في المعلّقة", show_alert=True)

# ══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(message):
    uid = message.from_user.id
    text = message.text
    u = ensure_user(uid, message.from_user.username,
                    message.from_user.first_name, message.from_user.last_name)
    if u.get("banned"): return

    # ══════════════════════════════════════════════════════════
    if is_admin(uid):
        st = admin_files_state.get(uid)

        if text == "📁 الملفات":
            send_admin_files(message.chat.id, uid, 0, None); return
        if text == "⏳ معلّق":
            send_admin_files(message.chat.id, uid, 0, "pending"); return
        if text == "🟢 شغال":
            send_admin_files(message.chat.id, uid, 0, "running"); return
        if text == "🔴 متوقف":
            send_admin_files(message.chat.id, uid, 0, "stopped"); return
        if text == "📋 الكل":
            send_admin_files(message.chat.id, uid, 0, None); return

        # ═══ ✨ قسم التنظيف الذكي ═══
        if text == "🧹 التنظيف الذكي":
            bot.send_message(message.chat.id,
                "🧹 <b>قسم التنظيف الذكي</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "تنظيف حقيقي للسيرفر — بدون وهم\n\n"
                "اختر من القائمة 👇",
                reply_markup=cleanup_menu_kb())
            return

        if text == "🤖 تحليل ذكي":
            msg = bot.send_message(message.chat.id, "🤖 جاري التحليل...")
            try:
                report = build_ai_report()
                bot.delete_message(message.chat.id, msg.message_id)
                bot.send_message(message.chat.id, report, reply_markup=cleanup_menu_kb())
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ خطأ: {e}", reply_markup=cleanup_menu_kb())
            return

        if text == "💾 عرض المساحة":
            total = get_dir_size(BASE_DIR)
            uploads = get_dir_size(UPLOADS_PATH)
            pending = get_dir_size(PENDING_PATH)
            logs = get_dir_size(LOGS_PATH)
            enc = get_dir_size(ENCRYPTED_PATH)
            local = get_dir_size(os.path.join(BASE_DIR, ".local"))
            disk_str = "غير متاح"
            try:
                d = shutil.disk_usage(BASE_DIR)
                disk_str = f"{d.used/(1024**3):.2f}/{d.total/(1024**3):.2f} GB ({d.used/d.total*100:.1f}%)"
            except: pass
            report = (
                f"💾 <b>حجم المساحات</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 المشروع الكامل: <b>{human_size(total)}</b>\n"
                f"📤 ملفات المستخدمين: <b>{human_size(uploads)}</b>\n"
                f"⏳ قائمة الانتظار: <b>{human_size(pending)}</b>\n"
                f"📋 السجلات: <b>{human_size(logs)}</b>\n"
                f"🔐 الملفات المشفرة: <b>{human_size(enc)}</b>\n"
                f"📚 مكتبات pip: <b>{human_size(local)}</b>\n\n"
                f"💻 القرص الكلي: <b>{disk_str}</b>"
            )
            bot.send_message(message.chat.id, report, reply_markup=cleanup_menu_kb())
            return

        if text == "⚡ تنظيف سريع":
            msg = bot.send_message(message.chat.id, "⚡ جاري التنظيف السريع...")
            try:
                c1, f1 = do_real_cleanup("logs")
                c2, f2 = do_real_cleanup("empty_folders")
                c3, f3 = do_real_cleanup("orphan_encrypted")
                total_c = c1 + c2 + c3
                total_f = f1 + f2 + f3
                bot.delete_message(message.chat.id, msg.message_id)
                bot.send_message(message.chat.id,
                    f"⚡ <b>انتهى التنظيف السريع</b>\n\n"
                    f"📋 عمليات: <b>{total_c}</b>\n"
                    f"💾 تم استرداد: <b>{human_size(total_f)}</b>",
                    reply_markup=cleanup_menu_kb())
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ خطأ: {e}", reply_markup=cleanup_menu_kb())
            return

        if text == "🔥 تنظيف شامل":
            msg = bot.send_message(message.chat.id,
                "🔥 <b>تنظيف شامل</b>\n\nجاري التنظيف العميق...\nانتظر قليلاً")
            try:
                c, f = do_real_cleanup("full")
                bot.delete_message(message.chat.id, msg.message_id)
                bot.send_message(message.chat.id,
                    f"🔥 <b>تم التنظيف الشامل</b>\n\n"
                    f"📋 عمليات: <b>{c}</b>\n"
                    f"💾 تم استرداد: <b>{human_size(f)}</b>\n\n"
                    f"✅ السيرفر أصبح أخف",
                    reply_markup=cleanup_menu_kb())
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ خطأ: {e}", reply_markup=cleanup_menu_kb())
            return

        if text == "📋 تنظيف السجلات":
            c, f = do_real_cleanup("logs")
            bot.send_message(message.chat.id,
                f"📋 <b>تنظيف السجلات</b>\n\n"
                f"✅ نظّف: <b>{c}</b> سجل\n"
                f"💾 استرجع: <b>{human_size(f)}</b>",
                reply_markup=cleanup_menu_kb())
            return

        if text == "📁 حذف المجلدات الفارغة":
            c, f = do_real_cleanup("empty_folders")
            bot.send_message(message.chat.id,
                f"📁 <b>حذف المجلدات الفارغة</b>\n\n"
                f"✅ حُذف: <b>{c}</b> مجلد",
                reply_markup=cleanup_menu_kb())
            return

        if text == "🔐 تنظيف التشفير المعلق":
            c, f = do_real_cleanup("orphan_encrypted")
            bot.send_message(message.chat.id,
                f"🔐 <b>تنظيف التشفير المعلق</b>\n\n"
                f"✅ حُذف: <b>{c}</b> ملف\n"
                f"💾 استرجع: <b>{human_size(f)}</b>",
                reply_markup=cleanup_menu_kb())
            return

        if text == "🗑️ حذف الملفات اليتيمة":
            c, f = do_real_cleanup("orphan_uploads")
            bot.send_message(message.chat.id,
                f"🗑️ <b>حذف اليتيمة</b>\n\n"
                f"✅ حُذف: <b>{c}</b> مجلد\n"
                f"💾 استرجع: <b>{human_size(f)}</b>",
                reply_markup=cleanup_menu_kb())
            return

        if text == "⏳ حذف المعلق القديم":
            c, f = do_real_cleanup("stale_pending")
            bot.send_message(message.chat.id,
                f"⏳ <b>حذف المعلق القديم</b>\n\n"
                f"✅ حُذف: <b>{c}</b> ملف",
                reply_markup=cleanup_menu_kb())
            return

        if text == "🔁 حذف المكررات":
            c, f = do_real_cleanup("duplicates")
            bot.send_message(message.chat.id,
                f"🔁 <b>حذف المكررات</b>\n\n"
                f"✅ حُذف: <b>{c}</b> ملف",
                reply_markup=cleanup_menu_kb())
            return

        if text == "🗑️ حذف المتوقفة القديمة":
            c, f = do_real_cleanup("stale_stopped")
            bot.send_message(message.chat.id,
                f"🗑️ <b>حذف المتوقفة القديمة (>7ي)</b>\n\n"
                f"✅ حُذف: <b>{c}</b> ملف",
                reply_markup=cleanup_menu_kb())
            return

        if text == "⚠️ حذف الفاشلة القديمة":
            c, f = do_real_cleanup("stale_failed")
            bot.send_message(message.chat.id,
                f"⚠️ <b>حذف الفاشلة القديمة (>3ي)</b>\n\n"
                f"✅ حُذف: <b>{c}</b> ملف",
                reply_markup=cleanup_menu_kb())
            return

        if text == "📚 حذف pip cache":
            msg = bot.send_message(message.chat.id, "📚 جاري حذف pip cache...")
            c, f = do_real_cleanup("pip_cache")
            bot.delete_message(message.chat.id, msg.message_id)
            bot.send_message(message.chat.id,
                f"📚 <b>حذف pip cache</b>\n\n"
                f"💾 استرجع: <b>{human_size(f)}</b>",
                reply_markup=cleanup_menu_kb())
            return

        if st:
            if text == "◀️ السابق":
                send_admin_files(message.chat.id, uid, st["page"] - 1, st["filter"]); return
            if text == "▶️ التالي":
                send_admin_files(message.chat.id, uid, st["page"] + 1, st["filter"]); return
            if text == "🔙 رجوع للقائمة":
                send_admin_files(message.chat.id, uid, st["page"], st["filter"]); return

        if text == "▶️ تشغيل الكل":
            c = 0
            for fid, f in list(db["files"].items()):
                if f.get("status") in ("approved", "stopped", "failed") and not is_process_running(fid):
                    if start_hosted_bot(fid)[0]: c += 1
            bot.send_message(message.chat.id, f"✅ شُغّل {c} ملف",
                             reply_markup=files_admin_kb()); return
        if text == "⏹ إيقاف الكل":
            c = 0
            for fid in list(db["files"].keys()):
                if is_process_running(fid): stop_hosted_bot(fid); c += 1
            bot.send_message(message.chat.id, f"⏹ أُوقف {c} ملف",
                             reply_markup=files_admin_kb()); return
        if text == "🗑️ حذف المتوقفة":
            c = 0
            for fid in list(db["files"].keys()):
                if not is_process_running(fid) and db["files"].get(fid, {}).get("status") != "pending":
                    if delete_file_full(fid): c += 1
            bot.send_message(message.chat.id, f"🗑️ حُذف {c} ملف",
                             reply_markup=files_admin_kb()); return

        if st and text in st.get("visible", {}):
            fid = st["visible"][text]
            send_admin_file_control(message.chat.id, uid, fid); return

        if st and st.get("sel_fid"):
            fid = st["sel_fid"]
            f = db["files"].get(fid)
            if f:
                if text in ("▶️ تشغيل", "⏹ إيقاف", "♻️ إعادة", "♻️ إعادة تشغيل"):
                    if text == "▶️ تشغيل": ok, m = start_hosted_bot(fid)
                    elif text == "⏹ إيقاف": stop_hosted_bot(fid); ok, m = True, "⏹ تم الإيقاف"
                    else: ok, m = restart_hosted_bot(fid)
                    bot.send_message(message.chat.id, m,
                                     reply_markup=admin_file_control_kb(fid)); return

                if text == "📋 السجل":
                    lp = os.path.join(LOGS_PATH, f"{fid}.log")
                    if not os.path.exists(lp) or not os.path.getsize(lp):
                        bot.send_message(message.chat.id, "📋 فارغ.",
                                         reply_markup=admin_file_control_kb(fid)); return
                    c_ = open(lp, "r", encoding="utf-8", errors="ignore").read()
                    c_ = c_[-3800:] if len(c_) > 3800 else c_
                    bot.send_message(message.chat.id,
                        f"📋 <b>السجل:</b>\n\n<pre>{html.escape(c_)}</pre>",
                        reply_markup=admin_file_control_kb(fid)); return

                if text == "⌨️ التيرمنال":
                    pending_action[uid] = {"action": "awaiting_terminal", "file": fid, "admin": True}
                    bot.send_message(message.chat.id, "⌨️ أرسل الأمر:", reply_markup=cancel_kb()); return

                if text == "📊 التفاصيل":
                    send_admin_file_control(message.chat.id, uid, fid); return

                if text in ("📝 تعديل", "📝 تعديل الكود"):
                    pending_action[uid] = {"action": "awaiting_new_code",
                                           "file": fid, "admin": True}
                    bot.send_message(message.chat.id, "📝 أرسل الكود الجديد:",
                                     reply_markup=cancel_kb()); return

                if text == "🔧 إصلاح":
                    p = f.get("path")
                    if not p or not os.path.exists(p):
                        bot.send_message(message.chat.id, "❌ غير موجود.",
                                         reply_markup=admin_file_control_kb(fid)); return
                    try:
                        with open(p, "r", encoding="utf-8") as fp: code = fp.read()
                        fixed = auto_fix_errors(code)
                        with open(p, "w", encoding="utf-8") as fp: fp.write(fixed)
                        if HAS_AES: save_encrypted(fid, fixed, f.get("owner"))
                        bot.send_message(message.chat.id, "🔧 تم الإصلاح.",
                                         reply_markup=admin_file_control_kb(fid))
                    except Exception as e:
                        bot.send_message(message.chat.id, f"❌ {e}")
                    return

                if text in ("🔑 التوكن", "🔑 تغيير التوكن"):
                    pending_action[uid] = {"action": "awaiting_new_token",
                                           "file": fid, "admin": True}
                    cur_tok = f.get("token") or "لا يوجد"
                    bot.send_message(message.chat.id,
                        f"🔑 <b>التوكن الحالي:</b>\n<code>{html.escape(cur_tok)}</code>\n\n"
                        f"أرسل التوكن الجديد أو اكتب <code>skip</code>:",
                        reply_markup=cancel_kb()); return

                if text in ("🆔 الآيدي", "🆔 تغيير الآيدي"):
                    pending_action[uid] = {"action": "awaiting_new_id",
                                           "file": fid, "admin": True}
                    try:
                        cur_id = extract_admin_id_from_file(f.get("path")) or "غير محدد"
                    except: cur_id = "غير محدد"
                    bot.send_message(message.chat.id,
                        f"🆔 <b>الآيدي الحالي:</b> <code>{html.escape(str(cur_id))}</code>\n\n"
                        f"أرسل الآيدي الجديد:",
                        reply_markup=cancel_kb()); return

                if text == "📥 تحميل":
                    p = f.get("path")
                    if not p or not os.path.exists(p):
                        bot.send_message(message.chat.id, "❌ غير موجود.",
                                         reply_markup=admin_file_control_kb(fid)); return
                    try:
                        with open(p, "rb") as fp:
                            bot.send_document(message.chat.id, fp,
                                caption=f"📄 {html.escape(f['filename'])}")
                    except Exception as e:
                        bot.send_message(message.chat.id, f"❌ {e}")
                    return

                if text == "🗑️ حذف":
                    pending_action[uid] = {"action": "confirm_delete_admin", "file": fid}
                    bot.send_message(message.chat.id, "⚠️ تأكيد الحذف؟",
                                     reply_markup=confirm_kb()); return

        # ═══ المستخدمين ═══
        if text == "👥 المستخدمين":
            bot.send_message(message.chat.id, "👥 قائمة المستخدمين:",
                             reply_markup=users_admin_kb()); return
        if text == "📋 آخر المستخدمين":
            m = f"👥 <b>آخر 15 مستخدم</b> ({len(db['users'])})\n\n"
            for uu, ud in list(db["users"].items())[-15:]:
                banned = "🚫" if ud.get("banned") else ("💎" if is_vip(int(uu)) else "•")
                m += f"{banned} <code>{uu}</code> · @{ud.get('username') or '—'} · {fmt_money(ud.get('balance', 0))}\n"
            bot.send_message(message.chat.id, m, reply_markup=users_admin_kb()); return
        if text == "🔍 بحث عضو":
            pending_action[uid] = {"action": "awaiting_member_id"}
            bot.send_message(message.chat.id, "🔍 أرسل آيدي أو @username:",
                             reply_markup=cancel_kb()); return

        mstate = admin_member_state.get(uid)
        if mstate and mstate.get("target"):
            t_uid = mstate["target"]
            t_user = db["users"].get(str(t_uid), {})
            if text == "➕ رصيد":
                pending_action[uid] = {"action": "add_money", "target": t_uid}
                bot.send_message(message.chat.id, "➕ كم؟", reply_markup=cancel_kb()); return
            if text == "➖ رصيد":
                pending_action[uid] = {"action": "sub_money", "target": t_uid}
                bot.send_message(message.chat.id, "➖ كم؟", reply_markup=cancel_kb()); return
            if text == "💰 تصفير":
                db["users"][str(t_uid)]["balance"] = 0; save_db()
                bot.send_message(message.chat.id, f"✅ تصفر رصيد <code>{t_uid}</code>",
                                 reply_markup=member_actions_kb())
                try: bot.send_message(t_uid, "⚠️ تم تصفير رصيدك.")
                except: pass
                return
            if text == "💎 منح VIP":
                pending_action[uid] = {"action": "grant_vip", "target": t_uid}
                bot.send_message(message.chat.id, "💎 عدد الأيام (0 = دائم):",
                                 reply_markup=cancel_kb()); return
            if text == "🆓 سحب VIP":
                db["users"][str(t_uid)]["is_vip"] = False
                db["users"][str(t_uid)]["vip_until"] = None; save_db()
                bot.send_message(message.chat.id, f"✅ سُحب VIP من <code>{t_uid}</code>",
                                 reply_markup=member_actions_kb())
                try: bot.send_message(t_uid, "⚠️ تم إلغاء VIP.")
                except: pass
                return
            if text == "🚫 حظر/فك":
                b = t_user.get("banned", False)
                db["users"][str(t_uid)]["banned"] = not b; save_db()
                bot.send_message(message.chat.id,
                    f"✅ {'فك حظره' if b else 'حظره'}",
                    reply_markup=member_actions_kb())
                try: bot.send_message(t_uid, "✅ فك الحظر." if b else "🚫 تم حظرك.")
                except: pass
                return
            if text == "📁 ملفاته":
                files = [(fid, f) for fid, f in db["files"].items()
                         if f.get("owner") == str(t_uid)]
                if not files:
                    bot.send_message(message.chat.id, "📁 لا ملفات.",
                                     reply_markup=member_actions_kb()); return
                m = f"📁 <b>ملفات</b> <code>{t_uid}</code>\n\n"
                for fid, f in files:
                    st = {"running":"🟢","stopped":"🔴","pending":"⏳","failed":"⚠️"}.get(f.get("status"),"•")
                    m += f"{st} <code>{html.escape(f['filename'])}</code>\n"
                bot.send_message(message.chat.id, m, reply_markup=member_actions_kb()); return
            if text == "🔙 رجوع":
                admin_member_state.pop(uid, None)
                bot.send_message(message.chat.id, "🔍 قائمة المستخدمين:",
                                 reply_markup=users_admin_kb()); return

        # ═══ الرصيد والعملة ═══
        if text == "💰 الرصيد والعملة":
            s = db["settings"]
            bot.send_message(message.chat.id,
                f"💰 <b>العملة</b>\n"
                f"💱 {html.escape(s.get('currency_name','نقطة'))}\n"
                f"🔣 {s.get('currency_symbol','💰')}",
                reply_markup=currency_menu_kb()); return
        if text == "💱 اسم العملة":
            pending_action[uid] = {"action": "set_currency_name"}
            bot.send_message(message.chat.id, "أرسل الاسم:", reply_markup=cancel_kb()); return
        if text == "🔣 الرمز":
            pending_action[uid] = {"action": "set_currency_symbol"}
            bot.send_message(message.chat.id, "أرسل الرمز:", reply_markup=cancel_kb()); return

        # ═══ الأسعار ═══
        if text == "⚙️ الأسعار":
            s = db["settings"]
            bot.send_message(message.chat.id,
                f"⚙️ <b>الأسعار</b>\n"
                f"📤 سعر الرفع: {fmt_money(s.get('upload_price',0))}\n"
                f"🎁 مكافأة الإحالة: {fmt_money(s.get('referral_reward',0))}",
                reply_markup=pricing_menu_kb()); return
        if text == "📤 سعر الرفع":
            pending_action[uid] = {"action": "set_upload_price"}
            bot.send_message(message.chat.id, f"أرسل السعر ({cur_name()}):",
                             reply_markup=cancel_kb()); return
        if text == "🎁 مكافأة الإحالة":
            pending_action[uid] = {"action": "set_referral_reward"}
            bot.send_message(message.chat.id, f"أرسل المكافأة ({cur_name()}):",
                             reply_markup=cancel_kb()); return

        # ═══ الترحيب ═══
        if text == "👋 الترحيب":
            s = db["settings"]
            mtype = s.get("welcome_media_type") or "بدون"
            bot.send_message(message.chat.id,
                f"👋 <b>الترحيب</b>\n"
                f"📝 {s.get('welcome_text','')[:200]}\n"
                f"🖼 {mtype}",
                reply_markup=welcome_menu_kb()); return
        if text == "📝 تعديل النص":
            pending_action[uid] = {"action": "awaiting_welcome_text"}
            bot.send_message(message.chat.id, "📝 أرسل النص:", reply_markup=cancel_kb()); return
        if text == "🖼 وسائط":
            pending_action[uid] = {"action": "awaiting_welcome_media"}
            bot.send_message(message.chat.id, "🖼 أرسل صورة/فيديو/GIF:", reply_markup=cancel_kb()); return
        if text == "🗑 حذف الوسائط":
            db["settings"]["welcome_media_type"] = None
            db["settings"]["welcome_media_id"] = None; save_db()
            bot.send_message(message.chat.id, "🗑 تم."); return
        if text == "👁 معاينة":
            wt = format_welcome_text(db["settings"]["welcome_text"], uid)
            try: bot.send_message(message.chat.id, wt)
            except: pass
            return
        if text == "📖 المتغيرات":
            bot.send_message(message.chat.id,
                "📖 <b>المتغيرات</b>\n\n"
                "<code>#name_user</code> · <code>#username</code>\n"
                "<code>#name</code> · <code>#id</code>\n"
                "<code>#points</code> · <code>#balance</code>\n"
                "<code>#currency</code> · <code>#symbol</code>\n"
                "<code>#invitelink</code> · <code>#bot_username</code>",
                reply_markup=welcome_menu_kb()); return
        if text == "🔄 الافتراضي":
            db["settings"]["welcome_text"] = DEFAULT_WELCOME
            db["settings"]["welcome_media_type"] = None
            db["settings"]["welcome_media_id"] = None; save_db()
            bot.send_message(message.chat.id, "🔄 تم."); return

        # ═══ الردود التلقائية ═══
        if text == "💬 الردود":
            send_auto_panel(message.chat.id, uid); return
        if text == "➕ إضافة رد":
            pending_action[uid] = {"action": "auto_add_kw"}
            bot.send_message(message.chat.id, "➕ أرسل الكلمة:", reply_markup=cancel_kb()); return
        if text == "❌ حذف الكل":
            db["settings"]["auto_replies"] = {}; save_db()
            bot.send_message(message.chat.id, "✅ تم."); return

        # ═══ القنوات ═══
        if text == "⚪ القنوات":
            chs = db["settings"]["channels"]
            m = "⚪ <b>القنوات الإجبارية</b>\n\n"
            if chs:
                for c in chs: m += f"• {html.escape(c)}\n"
            else: m += "لا توجد."
            bot.send_message(message.chat.id, m, reply_markup=channels_menu_kb()); return
        if text == "➕ إضافة":
            pending_action[uid] = {"action": "awaiting_channel"}
            bot.send_message(message.chat.id, "أرسل @username:", reply_markup=cancel_kb()); return
        if text == "🗑 حذف":
            chs = db["settings"]["channels"]
            if not chs:
                bot.send_message(message.chat.id, "لا قنوات."); return
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i, c in enumerate(chs): kb.add(f"🗑 {i+1}. {c}")
            kb.add("🔙 لوحة الإدارة")
            bot.send_message(message.chat.id, "اختر:", reply_markup=kb); return
        if text.startswith("🗑 ") and is_admin(uid) and "قناة" not in text:
            m = re.match(r"🗑 (\d+)\.", text)
            if m and "مشرف" not in text:
                i = int(m.group(1)) - 1
                chs = db["settings"]["channels"]
                if 0 <= i < len(chs):
                    removed = chs.pop(i); save_db()
                    bot.send_message(message.chat.id, f"✅ حُذف {removed}",
                                     reply_markup=channels_menu_kb()); return

        # ═══ المشرفين ═══
        if text == "👑 المشرفين":
            m = "👑 <b>المشرفين</b>\n\n"
            for a in ADMINS:
                tag = " (المالك)" if a == OWNER_ID else ""
                m += f"• <code>{a}</code>{tag}\n"
            bot.send_message(message.chat.id, m, reply_markup=admins_menu_kb()); return
        if text == "➕ إضافة مشرف" and is_owner(uid):
            pending_action[uid] = {"action": "awaiting_add_admin"}
            bot.send_message(message.chat.id, "أرسل الآيدي:", reply_markup=cancel_kb()); return
        if text == "🗑 حذف مشرف" and is_owner(uid):
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for a in ADMINS:
                if a != OWNER_ID: kb.add(f"🗑 مشرف {a}")
            kb.add("🔙 لوحة الإدارة")
            bot.send_message(message.chat.id, "اختر:", reply_markup=kb); return
        if text.startswith("🗑 مشرف ") and is_owner(uid):
            try:
                aid = int(text.replace("🗑 مشرف ", "").strip())
                if aid in ADMINS and aid != OWNER_ID:
                    ADMINS.discard(aid); save_db()
                    bot.send_message(message.chat.id, f"✅ حُذف {aid}",
                                     reply_markup=admins_menu_kb())
            except: pass
            return

        # ═══ السيرفر ═══
        if text == "📊 السيرفر":
            total_files = len(db["files"])
            running_count = sum(1 for fid in db["files"] if is_process_running(fid))
            stopped_count = total_files - running_count
            pending_count = sum(1 for f in db["files"].values() if f.get("status") == "pending")
            failed_count = sum(1 for f in db["files"].values() if f.get("status") == "failed")
            total_users = len(db["users"])
            vip_count = sum(1 for k in db["users"].keys() if is_vip(int(k)))
            banned_count = sum(1 for v in db["users"].values() if v.get("banned"))
            try:
                disk = shutil.disk_usage(BASE_DIR)
                disk_str = f"{disk.used/(1024**3):.1f}/{disk.total/(1024**3):.1f} GB ({disk.used/disk.total*100:.0f}%)"
            except: disk_str = "غير متاح"
            if psutil:
                try:
                    cpu = psutil.cpu_percent(interval=0.5)
                    cpu_cores = psutil.cpu_count()
                    mem = psutil.virtual_memory()
                    mem_used_mb = mem.used / (1024**2)
                    mem_total_mb = mem.total / (1024**2)
                    mem_pct = mem.percent
                    try:
                        boot = psutil.boot_time()
                        uptime = int(time.time() - boot)
                        days = uptime // 86400; hours = (uptime % 86400) // 3600; mins = (uptime % 3600) // 60
                        uptime_str = f"{days}ي {hours}س {mins}د"
                    except: uptime_str = "غير متاح"
                except:
                    cpu = 0; cpu_cores = 0; mem_pct = 0; mem_used_mb = 0; mem_total_mb = 0; uptime_str = "غير متاح"
            else:
                cpu = 0; cpu_cores = 0; mem_pct = 0; mem_used_mb = 0; mem_total_mb = 0; uptime_str = "غير متاح"
            aes_status = "✅ نشط" if HAS_AES else "❌ معطل"
            text_out = (
                f"📊 <b>حالة السيرفر</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>📁 الملفات:</b>\n"
                f"   📦 الإجمالي: <b>{total_files}</b>\n"
                f"   🟢 شغالة: <b>{running_count}</b>\n"
                f"   🔴 متوقفة: <b>{stopped_count}</b>\n"
                f"   ⏳ معلّقة: <b>{pending_count}</b>\n"
                f"   ⚠️ فاشلة: <b>{failed_count}</b>\n\n"
                f"<b>👥 المستخدمون:</b>\n"
                f"   👤 الإجمالي: <b>{total_users}</b>\n"
                f"   💎 VIP: <b>{vip_count}</b>\n"
                f"   🚫 محظور: <b>{banned_count}</b>\n\n"
                f"<b>💻 الموارد:</b>\n"
                f"   🧠 الذاكرة: <b>{mem_used_mb:.0f}/{mem_total_mb:.0f} MB ({mem_pct:.0f}%)</b>\n"
                f"   ⚙️ المعالج: <b>{cpu:.1f}%</b> · {cpu_cores} نواة\n"
                f"   💾 القرص: <b>{disk_str}</b>\n"
                f"   ⏱️ التشغيل: <b>{uptime_str}</b>\n\n"
                f"<b>🔧 النظام:</b>\n"
                f"   🐍 Python: <b>{platform.python_version()}</b>\n"
                f"   💻 النظام: <b>{platform.system()} {platform.machine()}</b>\n"
                f"   🔐 AES-256: <b>{aes_status}</b>\n"
            )
            bot.send_message(message.chat.id, text_out, reply_markup=admin_menu_kb()); return

        # ═══ الإذاعة ═══
        if text == "📢 إذاعة":
            pending_action[uid] = {"action": "awaiting_broadcast"}
            bot.send_message(message.chat.id, "📢 أرسل النص:", reply_markup=cancel_kb()); return

        # ═══ لوحة الإدارة ═══
        if text == "⚙️ لوحة الإدارة":
            bot.send_message(message.chat.id, "🛡️ لوحة الإدارة:",
                             reply_markup=admin_menu_kb()); return

    # ══════════════════════════════════════════════════════════
    ustate = user_files_state.get(uid)

    if text == "📁 ملفاتي":
        send_user_files(message.chat.id, uid); return

    if ustate and text in ustate.get("visible", {}):
        fid = ustate["visible"][text]
        send_user_file_control(message.chat.id, uid, fid); return

    if ustate and ustate.get("sel_fid"):
        fid = ustate["sel_fid"]
        f = db["files"].get(fid)
        if f and f.get("owner") == str(uid):
            if text in ("▶️ تشغيل", "⏹ إيقاف", "♻️ إعادة تشغيل", "♻️ إعادة"):
                if text == "▶️ تشغيل": ok, m = start_hosted_bot(fid)
                elif text == "⏹ إيقاف": stop_hosted_bot(fid); ok, m = True, "⏹ تم الإيقاف"
                else: ok, m = restart_hosted_bot(fid)
                bot.send_message(message.chat.id, m, reply_markup=user_file_control_kb(fid)); return
            if text == "📋 السجل":
                lp = os.path.join(LOGS_PATH, f"{fid}.log")
                if not os.path.exists(lp) or not os.path.getsize(lp):
                    bot.send_message(message.chat.id, "📋 فارغ.",
                                     reply_markup=user_file_control_kb(fid)); return
                c_ = open(lp, "r", encoding="utf-8", errors="ignore").read()
                c_ = c_[-3800:] if len(c_) > 3800 else c_
                bot.send_message(message.chat.id,
                    f"📋 <b>السجل:</b>\n\n<pre>{html.escape(c_)}</pre>",
                    reply_markup=user_file_control_kb(fid)); return
            if text == "⌨️ التيرمنال":
                pending_action[uid] = {"action": "awaiting_terminal", "file": fid}
                bot.send_message(message.chat.id, "⌨️ أرسل الأمر:", reply_markup=cancel_kb()); return
            if text == "📊 التفاصيل":
                send_user_file_control(message.chat.id, uid, fid); return
            if text == "📥 تحميل":
                p = f.get("path")
                if not p or not os.path.exists(p):
                    bot.send_message(message.chat.id, "❌ غير موجود.",
                                     reply_markup=user_file_control_kb(fid)); return
                try:
                    with open(p, "rb") as fp:
                        bot.send_document(message.chat.id, fp,
                            caption=f"📄 {html.escape(f['filename'])}")
                except Exception as e:
                    bot.send_message(message.chat.id, f"❌ {e}")
                return
            if text in ("📝 تعديل", "📝 تعديل الكود"):
                pending_action[uid] = {"action": "awaiting_new_code", "file": fid}
                bot.send_message(message.chat.id, "📝 أرسل الكود الجديد:",
                                 reply_markup=cancel_kb()); return
            if text == "🔧 إصلاح":
                p = f.get("path")
                if not p or not os.path.exists(p):
                    bot.send_message(message.chat.id, "❌ غير موجود.",
                                     reply_markup=user_file_control_kb(fid)); return
                try:
                    with open(p, "r", encoding="utf-8") as fp: code = fp.read()
                    fixed = auto_fix_errors(code)
                    with open(p, "w", encoding="utf-8") as fp: fp.write(fixed)
                    if HAS_AES: save_encrypted(fid, fixed, f.get("owner"))
                    bot.send_message(message.chat.id, "🔧 تم الإصلاح.",
                                     reply_markup=user_file_control_kb(fid))
                except Exception as e:
                    bot.send_message(message.chat.id, f"❌ {e}")
                return
            if text == "🔑 تغيير التوكن":
                pending_action[uid] = {"action": "awaiting_new_token", "file": fid}
                cur_tok = f.get("token") or "لا يوجد"
                bot.send_message(message.chat.id,
                    f"🔑 <b>التوكن الحالي:</b>\n<code>{html.escape(cur_tok)}</code>\n\n"
                    f"أرسل التوكن الجديد:",
                    reply_markup=cancel_kb()); return
            if text == "🆔 تغيير الآيدي":
                pending_action[uid] = {"action": "awaiting_new_id", "file": fid}
                try: cur_id = extract_admin_id_from_file(f.get("path")) or "غير محدد"
                except: cur_id = "غير محدد"
                bot.send_message(message.chat.id,
                    f"🆔 <b>الآيدي الحالي:</b> <code>{html.escape(str(cur_id))}</code>\n\n"
                    f"أرسل الآيدي الجديد:",
                    reply_markup=cancel_kb()); return
            if text == "🗑️ حذف":
                pending_action[uid] = {"action": "confirm_delete_user", "file": fid}
                bot.send_message(message.chat.id, "⚠️ تأكيد الحذف؟",
                                 reply_markup=confirm_kb()); return
            if text == "🔙 ملفاتي":
                send_user_files(message.chat.id, uid); return

    if text in ("📤 رفع ملف", "➕ رفع ملف"):
        if not is_owner(uid) and not is_vip(uid):
            price = int(db["settings"].get("upload_price", 0))
            if price > 0:
                bal = db["users"].get(str(uid), {}).get("balance", 0)
                if bal < price:
                    bot.send_message(message.chat.id,
                        f"❌ <b>رصيدك غير كافٍ</b>\n"
                        f"💰 {fmt_money(bal)} / {fmt_money(price)}",
                        reply_markup=main_menu_kb(uid))
                    return
        pending_action[uid] = {"action": "awaiting_file"}
        price_info = ""
        if not is_owner(uid) and not is_vip(uid):
            price = int(db["settings"].get("upload_price", 0))
            if price > 0: price_info = f"\n\n💰 سيُخصم: {fmt_money(price)}"
        if is_owner(uid):
            price_info += "\n\n⚡ <b>كمالك — سيشتغل فوراً بدون انتظار</b>"
        bot.send_message(message.chat.id,
            f"📤 أرسل ملف .py:{price_info}",
            reply_markup=cancel_kb()); return

    if text == "👤 حسابي":
        c_files = sum(1 for f in db["files"].values() if f.get("owner") == str(uid))
        c_run = sum(1 for fid, f in db["files"].items()
                    if f.get("owner") == str(uid) and is_process_running(fid))
        c_refs = sum(1 for u_ in db["users"].values() if u_.get("referrer") == str(uid))
        vip_tag = "💎 VIP" if is_vip(uid) else "🆓 مجاني"
        bot.send_message(message.chat.id,
            f"👤 <b>حسابي</b>\n"
            f"🆔 <code>{uid}</code>\n"
            f"📛 @{u.get('username') or '—'}\n"
            f"💠 <b>{vip_tag}</b>\n"
            f"💰 {fmt_money(u.get('balance', 0))}\n"
            f"🎁 {c_refs} إحالة\n"
            f"📁 {c_files} ملف ({c_run} شغال)",
            reply_markup=main_menu_kb(uid)); return

    if text == "📊 إحصائياتي":
        c_files = sum(1 for f in db["files"].values() if f.get("owner") == str(uid))
        c_run = sum(1 for fid, f in db["files"].items()
                    if f.get("owner") == str(uid) and is_process_running(fid))
        c_pend = sum(1 for f in db["files"].values()
                     if f.get("owner") == str(uid) and f.get("status") == "pending")
        bot.send_message(message.chat.id,
            f"📊 <b>إحصائياتي</b>\n"
            f"📁 {c_files} · 🟢 {c_run} · 🔴 {c_files-c_run-c_pend} · ⏳ {c_pend}",
            reply_markup=main_menu_kb(uid)); return

    if text == "🎁 دعوة صديق":
        bU = BOT_USERNAME or "unknown"
        link = f"https://t.me/{bU}?start={uid}"
        reward = int(db["settings"].get("referral_reward", 0))
        c_refs = sum(1 for u_ in db["users"].values() if u_.get("referrer") == str(uid))
        bot.send_message(message.chat.id,
            f"🎁 <b>دعوة صديق</b>\n\n"
            f"🔗 <code>{link}</code>\n\n"
            f"💰 المكافأة: {fmt_money(reward)}\n"
            f"🎯 إحالاتك: {c_refs}",
            reply_markup=main_menu_kb(uid)); return

    if text == "📖 التعليمات":
        price = int(db["settings"].get("upload_price", 0))
        bot.send_message(message.chat.id,
            f"📖 <b>التعليمات</b>\n\n"
            f"1️⃣ رفع ملف .py\n"
            f"2️⃣ انتظار الموافقة\n"
            f"3️⃣ تحكم كامل من 📁 ملفاتي\n\n"
            f"💰 سعر الرفع: {fmt_money(price) if price else 'مجاني'}\n"
            f"🔐 ملفاتك مشفرة AES-256",
            reply_markup=main_menu_kb(uid)); return

    if text == "💬 الدعم الفني":
        pending_action[uid] = {"action": "awaiting_question"}
        bot.send_message(message.chat.id, "💬 اكتب رسالتك:", reply_markup=cancel_kb()); return

    if text == "🔙 القائمة" or text == "🔙 القائمة الرئيسية" or text == "🔙 رجوع":
        pending_action.pop(uid, None)
        user_files_state.pop(uid, None)
        admin_files_state.pop(uid, None)
        admin_member_state.pop(uid, None)
        if is_admin(uid) and text == "🔙 لوحة الإدارة":
            bot.send_message(message.chat.id, "🛡️ لوحة الإدارة:",
                             reply_markup=admin_menu_kb())
        else:
            bot.send_message(message.chat.id, "📋 القائمة الرئيسية:",
                             reply_markup=main_menu_kb(uid))
        return

    if text == "🔙 لوحة الإدارة":
        pending_action.pop(uid, None)
        admin_files_state.pop(uid, None)
        admin_member_state.pop(uid, None)
        bot.send_message(message.chat.id, "🛡️ لوحة الإدارة:",
                         reply_markup=admin_menu_kb()); return

    if text == "🔙 ملفاتي":
        user_files_state.pop(uid, None)
        send_user_files(message.chat.id, uid); return

    if text == "🔙 رجوع للقائمة" and is_admin(uid):
        st = admin_files_state.get(uid)
        if st:
            send_admin_files(message.chat.id, uid, st.get("page", 0), st.get("filter"))
        else:
            bot.send_message(message.chat.id, "🛡️ لوحة الإدارة:",
                             reply_markup=admin_menu_kb())
        return

    if text == "❌ إلغاء":
        pending_action.pop(uid, None)
        kb = admin_menu_kb() if is_admin(uid) else main_menu_kb(uid)
        bot.send_message(message.chat.id, "❌ إلغاء.", reply_markup=kb); return

    # ══════════════════════════════════════════════════════════
    if uid in pending_action:
        act = pending_action[uid].get("action")

        if act == "awaiting_terminal":
            fid = pending_action[uid].get("file")
            admin_mode = pending_action[uid].get("admin", False)
            f = db["files"].get(fid)
            if not f or (not admin_mode and f.get("owner") != str(uid)):
                bot.send_message(message.chat.id, "❌ غير مصرح.")
                pending_action.pop(uid, None); return
            if write_proc(fid, text):
                bot.send_message(message.chat.id,
                    f"✅ <code>{html.escape(text[:200])}</code>",
                    reply_markup=admin_file_control_kb(fid) if admin_mode
                    else user_file_control_kb(fid))
            else:
                bot.send_message(message.chat.id, "❌ البوت غير شغال.",
                    reply_markup=admin_file_control_kb(fid) if admin_mode
                    else user_file_control_kb(fid))
            pending_action.pop(uid, None); return

        if act == "awaiting_new_token":
            fid = pending_action[uid].get("file")
            admin_mode = pending_action[uid].get("admin", False)
            f = db["files"].get(fid)
            if not f or (not admin_mode and f.get("owner") != str(uid)):
                bot.send_message(message.chat.id, "❌ غير مصرح.")
                pending_action.pop(uid, None); return
            new_token = text.strip()
            if new_token.lower() == "skip":
                bot.send_message(message.chat.id, "⏭️ تم التخطي.",
                    reply_markup=admin_file_control_kb(fid) if admin_mode
                    else user_file_control_kb(fid))
                pending_action.pop(uid, None); return
            if not re.match(r'^\d{8,12}:[A-Za-z0-9_\-]{30,50}$', new_token):
                bot.send_message(message.chat.id, "❌ صيغة التوكن غير صحيحة.",
                                 reply_markup=cancel_kb()); return
            try:
                p = f.get("path")
                if not p or not os.path.exists(p):
                    bot.send_message(message.chat.id, "❌ الملف غير موجود.")
                    pending_action.pop(uid, None); return
                with open(p, "r", encoding="utf-8") as fp: code = fp.read()
                updated = update_token_in_content(code, new_token)
                with open(p, "w", encoding="utf-8") as fp: fp.write(updated)
                if HAS_AES: save_encrypted(fid, updated, f.get("owner"))
                f["token"] = new_token
                info = get_bot_info_from_token(new_token)
                if info:
                    f["bot_username"] = info.get("username")
                    f["bot_name"] = info.get("first_name")
                    f["bot_id"] = info.get("id")
                save_db()
                pending_action.pop(uid, None)
                bot.send_message(message.chat.id,
                    f"✅ تم تحديث التوكن\n"
                    f"{'🤖 @' + info['username'] if info else ''}",
                    reply_markup=admin_file_control_kb(fid) if admin_mode
                    else user_file_control_kb(fid))
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ {e}")
            return

        if act == "awaiting_new_id":
            fid = pending_action[uid].get("file")
            admin_mode = pending_action[uid].get("admin", False)
            f = db["files"].get(fid)
            if not f or (not admin_mode and f.get("owner") != str(uid)):
                bot.send_message(message.chat.id, "❌ غير مصرح.")
                pending_action.pop(uid, None); return
            new_id = text.strip()
            if new_id.lower() == "skip":
                bot.send_message(message.chat.id, "⏭️ تم التخطي.",
                    reply_markup=admin_file_control_kb(fid) if admin_mode
                    else user_file_control_kb(fid))
                pending_action.pop(uid, None); return
            if not new_id.isdigit() or len(new_id) < 7:
                bot.send_message(message.chat.id, "❌ آيدي غير صحيح (رقم 7+ خانات).",
                                 reply_markup=cancel_kb()); return
            try:
                p = f.get("path")
                if not p or not os.path.exists(p):
                    bot.send_message(message.chat.id, "❌ الملف غير موجود.")
                    pending_action.pop(uid, None); return
                with open(p, "r", encoding="utf-8") as fp: code = fp.read()
                updated = update_admin_id_in_content(code, new_id)
                with open(p, "w", encoding="utf-8") as fp: fp.write(updated)
                if HAS_AES: save_encrypted(fid, updated, f.get("owner"))
                save_db()
                pending_action.pop(uid, None)
                bot.send_message(message.chat.id,
                    f"✅ تم تحديث الآيدي: <code>{new_id}</code>",
                    reply_markup=admin_file_control_kb(fid) if admin_mode
                    else user_file_control_kb(fid))
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ {e}")
            return

        if act == "awaiting_new_code":
            fid = pending_action[uid].get("file")
            f = db["files"].get(fid)
            admin_mode = pending_action[uid].get("admin", False)
            if not f or (not admin_mode and f.get("owner") != str(uid)):
                bot.send_message(message.chat.id, "❌ غير مصرح.")
                pending_action.pop(uid, None); return
            try:
                with open(f["path"], "w", encoding="utf-8") as fp: fp.write(text)
                if HAS_AES: save_encrypted(fid, text, f.get("owner"))
                nt = extract_token_from_file(f["path"])
                if nt:
                    f["token"] = nt
                    info = get_bot_info_from_token(nt)
                    if info:
                        f["bot_username"] = info.get("username")
                        f["bot_name"] = info.get("first_name")
                        f["bot_id"] = info.get("id")
                save_db(); pending_action.pop(uid, None)
                ok, m = restart_hosted_bot(fid)
                bot.send_message(message.chat.id, m,
                    reply_markup=admin_file_control_kb(fid) if admin_mode
                    else user_file_control_kb(fid))
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ {e}")
            return

        if act == "set_currency_name":
            val = text.strip()[:20]
            if not val: bot.send_message(message.chat.id, "❌ فارغ."); return
            db["settings"]["currency_name"] = val; save_db()
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, f"✅ {html.escape(val)}",
                             reply_markup=currency_menu_kb()); return

        if act == "set_currency_symbol":
            val = text.strip()[:5]
            if not val: bot.send_message(message.chat.id, "❌ فارغ."); return
            db["settings"]["currency_symbol"] = val; save_db()
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, f"✅ {html.escape(val)}",
                             reply_markup=currency_menu_kb()); return

        if act == "set_upload_price":
            try: val = int(text.strip()); assert val >= 0
            except: bot.send_message(message.chat.id, "❌ رقم غير صحيح."); return
            db["settings"]["upload_price"] = val; save_db()
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, f"✅ {fmt_money(val)}",
                             reply_markup=pricing_menu_kb()); return

        if act == "set_referral_reward":
            try: val = int(text.strip()); assert val >= 0
            except: bot.send_message(message.chat.id, "❌ رقم غير صحيح."); return
            db["settings"]["referral_reward"] = val; save_db()
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, f"✅ {fmt_money(val)}",
                             reply_markup=pricing_menu_kb()); return

        if act == "awaiting_member_id":
            q = text.strip().lstrip("@")
            found_uid = None
            if q.isdigit() and q in db["users"]:
                found_uid = int(q)
            else:
                for k, v in db["users"].items():
                    if (v.get("username") or "").lower() == q.lower():
                        found_uid = int(k); break
            if not found_uid:
                bot.send_message(message.chat.id, "❌ غير موجود.",
                                 reply_markup=cancel_kb()); return
            uu = db["users"][str(found_uid)]
            files = [(fid, f) for fid, f in db["files"].items()
                     if f.get("owner") == str(found_uid)]
            running = sum(1 for fid, f in files if is_process_running(fid))
            admin_member_state[uid] = {"target": found_uid}
            pending_action.pop(uid, None)
            vip_tag = "💎 VIP" if is_vip(found_uid) else "🆓 مجاني"
            bot.send_message(message.chat.id,
                f"👤 <b>عضو</b>\n"
                f"🆔 <code>{found_uid}</code>\n"
                f"📛 @{uu.get('username') or '—'}\n"
                f"💠 {vip_tag}\n"
                f"💰 {fmt_money(uu.get('balance', 0))}\n"
                f"📁 {len(files)} ملف ({running} شغال)",
                reply_markup=member_actions_kb()); return

        if act == "add_money":
            t_uid = pending_action[uid].get("target")
            try: val = int(text.strip()); assert val > 0
            except: bot.send_message(message.chat.id, "❌ رقم غير صحيح."); return
            if str(t_uid) not in db["users"]:
                pending_action.pop(uid, None); return
            db["users"][str(t_uid)]["balance"] = db["users"][str(t_uid)].get("balance", 0) + val
            save_db(); pending_action.pop(uid, None)
            nb = db["users"][str(t_uid)]["balance"]
            bot.send_message(message.chat.id, f"✅ +{fmt_money(val)} → {fmt_money(nb)}",
                             reply_markup=member_actions_kb())
            try: bot.send_message(int(t_uid), f"🎁 +{fmt_money(val)}\n💼 {fmt_money(nb)}")
            except: pass
            return

        if act == "sub_money":
            t_uid = pending_action[uid].get("target")
            try: val = int(text.strip()); assert val > 0
            except: bot.send_message(message.chat.id, "❌ رقم غير صحيح."); return
            if str(t_uid) not in db["users"]:
                pending_action.pop(uid, None); return
            cur = db["users"][str(t_uid)].get("balance", 0)
            nb = max(0, cur - val)
            db["users"][str(t_uid)]["balance"] = nb; save_db()
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, f"✅ -{fmt_money(val)} → {fmt_money(nb)}",
                             reply_markup=member_actions_kb())
            try: bot.send_message(int(t_uid), f"⚠️ -{fmt_money(val)}\n💼 {fmt_money(nb)}")
            except: pass
            return

        if act == "grant_vip":
            t_uid = pending_action[uid].get("target")
            try: days = int(text.strip()); assert days >= 0
            except: bot.send_message(message.chat.id, "❌ رقم غير صحيح."); return
            if str(t_uid) not in db["users"]:
                pending_action.pop(uid, None); return
            if days == 0:
                db["users"][str(t_uid)]["is_vip"] = True
                db["users"][str(t_uid)]["vip_until"] = None
                txt = "دائم ♾"
            else:
                until = (datetime.now() + timedelta(days=days)).isoformat()
                db["users"][str(t_uid)]["is_vip"] = True
                db["users"][str(t_uid)]["vip_until"] = until
                txt = f"{days} يوم"
            save_db(); pending_action.pop(uid, None)
            bot.send_message(message.chat.id, f"💎 VIP: {txt}",
                             reply_markup=member_actions_kb())
            try: bot.send_message(int(t_uid), f"💎 تم ترقيتك!\n⏰ {txt}")
            except: pass
            return

        if act == "awaiting_add_admin" and is_owner(uid):
            try:
                aid = int(text.strip())
                ADMINS.add(aid)
                if aid not in db.get("admins", []):
                    db.setdefault("admins", []).append(aid)
                save_db()
                bot.send_message(message.chat.id, f"✅ {aid}",
                                 reply_markup=admins_menu_kb())
            except:
                bot.send_message(message.chat.id, "❌ آيدي غلط.",
                                 reply_markup=admins_menu_kb())
            pending_action.pop(uid, None); return

        if act == "awaiting_broadcast" and is_admin(uid):
            c = 0
            for u2 in list(db["users"].keys()):
                try:
                    bot.send_message(int(u2), f"📢 <b>إعلان</b>\n\n{text}"); c += 1
                    time.sleep(0.05)
                except: pass
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, f"✅ {c} مستخدم",
                             reply_markup=admin_menu_kb()); return

        if act == "awaiting_question":
            un = message.from_user.username or ""
            bot.send_message(OWNER_ID,
                f"💬 <b>دعم</b>\n@{un} (<code>{uid}</code>)\n\n{html.escape(text)}")
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, "✅ أُرسلت.",
                             reply_markup=main_menu_kb(uid)); return

        if act == "awaiting_channel" and is_admin(uid):
            ch = text.strip()
            if not ch.startswith("@"): ch = "@" + ch
            db["settings"]["channels"].append(ch); save_db()
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, f"✅ {ch}",
                             reply_markup=channels_menu_kb()); return

        if act == "auto_add_kw" and is_admin(uid):
            kw = text.strip()
            if not kw: bot.send_message(message.chat.id, "⚠️ فارغة."); return
            pending_action[uid] = {"action": "auto_add_content", "keyword": kw}
            bot.send_message(message.chat.id, f"✅ <code>{html.escape(kw)}</code>\nالرد:",
                             reply_markup=cancel_kb()); return

        if act == "auto_add_content" and is_admin(uid):
            kw = pending_action[uid]["keyword"]
            try: content = message.html_text
            except: content = text
            db["settings"]["auto_replies"][kw] = {"content": content}
            save_db(); pending_action.pop(uid, None)
            bot.send_message(message.chat.id, "✅ تم.")
            send_auto_panel(message.chat.id, uid); return

        if act == "awaiting_welcome_text" and is_admin(uid):
            try: ht = message.html_text
            except: ht = text
            db["settings"]["welcome_text"] = ht; save_db()
            pending_action.pop(uid, None)
            bot.send_message(message.chat.id, "✅ تم."); return

        if act == "confirm_delete_user":
            if text == "✅ نعم":
                fid = pending_action[uid].get("file")
                delete_file_full(fid)
                pending_action.pop(uid, None)
                bot.send_message(message.chat.id, "🗑️ تم.",
                                 reply_markup=main_menu_kb(uid))
            elif text == "❌ لا":
                pending_action.pop(uid, None)
                send_user_files(message.chat.id, uid)
            return

        if act == "confirm_delete_admin":
            if text == "✅ نعم":
                fid = pending_action[uid].get("file")
                delete_file_full(fid)
                pending_action.pop(uid, None)
                bot.send_message(message.chat.id, "🗑️ تم.",
                                 reply_markup=admin_menu_kb())
            elif text == "❌ لا":
                fid = pending_action[uid].get("file")
                pending_action.pop(uid, None)
                send_admin_file_control(message.chat.id, uid, fid)
            return

    if text and not text.startswith("/") and not is_admin(uid) and uid not in pending_action:
        for kw, rep in db["settings"]["auto_replies"].items():
            if kw in text:
                try:
                    bot.send_message(message.chat.id,
                        format_reply_text(rep.get("content", ""), uid))
                except: pass
                break

# ══════════════════════════════════════════════════════════════
def send_auto_panel(chat_id, uid):
    ars = db["settings"]["auto_replies"]
    m = "💬 <b>الردود التلقائية</b>\n"
    if ars:
        m += f"عدد: {len(ars)}\n\n"
        for i, k in enumerate(ars.keys(), 1):
            m += f"{i}. <code>{html.escape(k)}</code>\n"
    else:
        m += "لا توجد."
    bot.send_message(chat_id, m, reply_markup=auto_replies_menu_kb(uid))

# ══════════════════════════════════════════════════════════════
@bot.message_handler(content_types=["document"])
def handle_doc(message):
    uid = message.from_user.id
    action = pending_action.get(uid, {}).get("action")

    if action in ("awaiting_new_code", "awaiting_new_token", "awaiting_new_id"):
        bot.reply_to(message, "❌ أرسل نصاً وليس ملفاً."); return

    if action != "awaiting_file":
        bot.reply_to(message, "❌ اضغط 📤 رفع ملف أولاً."); return
    doc = message.document
    if os.path.splitext(doc.file_name)[1].lower() != ".py":
        bot.reply_to(message, "❌ .py فقط."); return

    price = 0
    if not is_owner(uid) and not is_vip(uid):
        price = int(db["settings"].get("upload_price", 0))
        if price > 0:
            bal = db["users"].get(str(uid), {}).get("balance", 0)
            if bal < price:
                bot.reply_to(message,
                    f"❌ <b>رصيدك غير كافٍ</b>\n💰 {fmt_money(bal)} / {fmt_money(price)}",
                    reply_markup=main_menu_kb(uid))
                pending_action.pop(uid, None); return

    fi = bot.get_file(doc.file_id)
    data = bot.download_file(fi.file_path)
    fid = short_id()
    base_name = os.path.splitext(doc.file_name)[0]
    folder_name = get_unique_folder_name(uid, base_name)

    up = os.path.join(PENDING_PATH, str(uid))
    bf = os.path.join(up, folder_name)
    os.makedirs(bf, exist_ok=True)
    pf = os.path.join(bf, doc.file_name)
    with open(pf, "wb") as f: f.write(data)

    try: install_for_bot(pf)
    except: pass

    token = extract_token_from_file(pf)
    bi = get_bot_info_from_token(token) if token else None

    if price > 0 and not is_owner(uid) and not is_vip(uid):
        db["users"][str(uid)]["balance"] = db["users"][str(uid)].get("balance", 0) - price

    # ⚡ المالك — تشغيل فوري بدون انتظار
    if is_owner(uid):
        try:
            uu = os.path.join(UPLOADS_PATH, str(uid))
            bf2 = os.path.join(uu, folder_name)
            os.makedirs(bf2, exist_ok=True)
            final_path = os.path.join(bf2, doc.file_name)
            shutil.move(pf, final_path)
            try:
                pd = os.path.dirname(pf)
                if os.path.exists(pd) and not os.listdir(pd): os.rmdir(pd)
                pu = os.path.dirname(pd)
                if os.path.exists(pu) and not os.listdir(pu): os.rmdir(pu)
            except: pass
            if HAS_AES:
                try: save_encrypted(fid, data.decode("utf-8", errors="ignore"), uid)
                except: pass
            db["files"][fid] = {
                "owner": str(uid), "filename": doc.file_name,
                "folder": folder_name, "path": final_path,
                "status": "approved",
                "uploaded_at": now_iso(), "pid": None, "token": token,
                "bot_username": bi.get("username") if bi else None,
                "bot_name": bi.get("first_name") if bi else None,
                "bot_id": bi.get("id") if bi else None,
            }
            save_db(); pending_action.pop(uid, None)
            ok, m = start_hosted_bot(fid)
            extra = f"\n🤖 @{html.escape(bi['username'])}" if bi else ""
            bot.send_message(message.chat.id,
                f"⚡ <b>تم الرفع والتشغيل فوراً</b>\n\n"
                f"📄 <code>{html.escape(doc.file_name)}</code>{extra}\n"
                f"⚙️ {m}",
                reply_markup=main_menu_kb(uid))
            return
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطأ في التشغيل التلقائي: {e}")
            pending_action.pop(uid, None); return

    # مستخدم عادي — يبقى معلقاً
    db["files"][fid] = {
        "owner": str(uid), "filename": doc.file_name,
        "folder": folder_name, "pending_path": pf,
        "path": None, "status": "pending",
        "uploaded_at": now_iso(), "pid": None, "token": token,
        "bot_username": bi.get("username") if bi else None,
        "bot_name": bi.get("first_name") if bi else None,
        "bot_id": bi.get("id") if bi else None,
    }
    save_db(); pending_action.pop(uid, None)

    extra = ""
    if bi: extra = f"\n\n🤖 @{html.escape(bi['username'] or '—')}"
    paid_info = ""
    if price > 0 and not is_owner(uid) and not is_vip(uid):
        nb = db["users"][str(uid)].get("balance", 0)
        paid_info = f"\n💰 خُصم: {fmt_money(price)}\n💼 رصيدك: {fmt_money(nb)}"

    bot.send_message(message.chat.id,
        f"✅ تم الاستلام\n\n"
        f"📄 <b>{html.escape(doc.file_name)}</b>{extra}{paid_info}\n\n"
        f"⏳ قيد المراجعة.",
        reply_markup=main_menu_kb(uid))

    user = message.from_user
    uname = f"@{user.username}" if user.username else "بدون"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    size_kb = len(data) / 1024
    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"

    notif = (
        f"📤 <b>طلب رفع جديد</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>المستخدم:</b> {html.escape(full_name) or 'غير معروف'}\n"
        f"📛 <b>اليوزر:</b> {uname}\n"
        f"🆔 <b>الآيدي:</b> <code>{uid}</code>\n"
        f"💼 <b>رصيده:</b> {fmt_money(db['users'].get(str(uid), {}).get('balance', 0))}\n"
        f"💎 <b>الرتبة:</b> {'VIP' if is_vip(uid) else 'مجاني'}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📄 <b>الملف:</b> <code>{html.escape(doc.file_name)}</code>\n"
        f"📁 <b>المجلد:</b> <code>{html.escape(folder_name)}</code>\n"
        f"📦 <b>الحجم:</b> {size_str}"
    )
    if bi:
        notif += f"\n🤖 <b>البوت:</b> @{html.escape(bi['username'] or '—')}"
    elif token:
        notif += "\n⚠️ توكن موجود (لم يُتحقق)"
    else:
        notif += "\n⚠️ لا يوجد توكن"

    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.row(
        types.InlineKeyboardButton("✅ قبول", callback_data=f"pend_accept_{fid}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"pend_reject_{fid}"),
        types.InlineKeyboardButton("⏭️ ترك", callback_data=f"pend_leave_{fid}")
    )

    try:
        bot.send_message(OWNER_ID, notif, reply_markup=kb)
    except Exception as e:
        print(f"notif err: {e}")

@bot.message_handler(content_types=["photo", "video", "animation"])
def handle_media(message):
    uid = message.from_user.id
    if pending_action.get(uid, {}).get("action") != "awaiting_welcome_media": return
    if not is_admin(uid): return
    if message.photo:
        db["settings"]["welcome_media_type"] = "photo"
        db["settings"]["welcome_media_id"] = message.photo[-1].file_id
    elif message.video:
        db["settings"]["welcome_media_type"] = "video"
        db["settings"]["welcome_media_id"] = message.video.file_id
    elif message.animation:
        db["settings"]["welcome_media_type"] = "animation"
        db["settings"]["welcome_media_id"] = message.animation.file_id
    save_db(); pending_action.pop(uid, None)
    bot.send_message(message.chat.id, "✅ تم.")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("🗑 ") and is_admin(m.from_user.id))
def handle_delete_reply(message):
    uid = message.from_user.id
    if "قناة" in message.text or "مشرف" in message.text: return
    m = re.match(r"🗑 (\d+)\.", message.text)
    if not m: return
    idx = int(m.group(1)) - 1
    ars = db["settings"]["auto_replies"]
    keys = list(ars.keys())
    if 0 <= idx < len(keys):
        kw = keys[idx]
        ars.pop(kw, None); save_db()
        bot.send_message(message.chat.id, f"✅ حُذف: {kw}")
        send_auto_panel(message.chat.id, uid)

# ══════════════════════════════════════════════════════════════
def monitor_processes():
    while True:
        time.sleep(30)
        try:
            for fid, f in list(db["files"].items()):
                if f.get("status") == "running":
                    proc = running_processes.get(fid)
                    if proc and proc.poll() is not None:
                        f["status"] = "stopped"; f["pid"] = None
                        save_db()
                        running_processes.pop(fid, None)
                        owner = f.get("owner")
                        if owner and owner != "None":
                            try:
                                bot.send_message(int(owner),
                                    f"⚠️ توقف ملفك:\n<code>{html.escape(f['filename'])}</code>")
                            except: pass
        except Exception as e:
            print(f"monitor: {e}")

def log_cleaner():
    while True:
        time.sleep(LOG_CLEAN_INTERVAL)
        try:
            cleaned = 0
            for lp in _glob.glob(os.path.join(LOGS_PATH, "*.log")):
                try:
                    sz = os.path.getsize(lp)
                    if sz < 50 * 1024: continue
                    with open(lp, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    if len(lines) > 500:
                        with open(lp, "w", encoding="utf-8") as f:
                            f.writelines(lines[-500:])
                        cleaned += 1
                except: pass
            if cleaned:
                print(f"🧹 نظّف {cleaned} سجل")
        except Exception as e:
            print(f"log_cleaner: {e}")

threading.Thread(target=monitor_processes, daemon=True).start()
threading.Thread(target=log_cleaner, daemon=True).start()

# ══════════════════════════════════════════════════════════════
def run_bot_safely():
    global BOT_USERNAME
    for d in (UPLOADS_PATH, LOGS_PATH, PENDING_PATH, ENCRYPTED_PATH):
        os.makedirs(d, exist_ok=True)

    print("🔍 فحص التوكن...")
    try:
        me = bot.get_me()
        BOT_USERNAME = me.username
        print(f"✅ @{BOT_USERNAME}")
    except Exception as e:
        print(f"❌ فشل الاتصال بالتوكن: {e}")
        time.sleep(5)
        return

    if HAS_AES:
        init_security()
        print("🔐 AES-256 نشط")
    else:
        print("⚠️ التشفير معطل")

    saved_admins = db.get("admins", [])
    for a in saved_admins:
        try: ADMINS.add(int(a))
        except: pass
    ADMINS.add(OWNER_ID)

    try:
        bot.send_message(OWNER_ID,
            f"🚀 <b>البوت يعمل</b>\n"
            f"🤖 @{BOT_USERNAME}\n"
            f"🔐 AES: {'✅' if HAS_AES else '❌'}\n"
            f"🛡️ درع حماية السيرفر: نشط\n"
            f"🧹 تنظيف السجل كل {LOG_CLEAN_INTERVAL//60} دقيقة\n"
            f"⚡ المالك يرفع مباشرة بدون انتظار",
            disable_notification=True)
    except: pass

    for fid, f in db["files"].items():
        if f.get("status") == "running":
            print(f"🔄 إعادة تشغيل {f['filename']}...")
            start_hosted_bot(fid)

    print("🤖 البوت يعمل...")
    # 🛡️ إعدادات تقليل استهلاك المعالج
    bot.infinity_polling(skip_pending=True, timeout=30, none_stop=True, long_polling_timeout=30)

# 🛡️ درع عدم الاستسلام (إذا انهار الكود لأي سبب، يعيد التشغيل تلقائياً)
if __name__ == "__main__":
    while True:
        try:
            run_bot_safely()
        except KeyboardInterrupt:
            print("\n🛑 تم الإيقاف يدوياً بواسطة المطور.")
            break
        except Exception as e:
            print(f"\n⚠️ انهيار غير متوقع: {e}")
            print("🔄 جاري إعادة التشغيل تلقائياً بعد 5 ثوانٍ...")
            time.sleep(5)