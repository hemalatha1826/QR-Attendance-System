import streamlit as st
import pandas as pd
import json, os
from datetime import date, datetime
import qrcode
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Auxilium College - QR Attendance", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f1b35,#1a2a4a);}
[data-testid="stSidebar"] *{color:#e0e8ff!important;}
.main .block-container{background:#0d1b2e;padding-top:2rem;}
.metric-card{background:linear-gradient(135deg,#1a2a4a,#243560);border-radius:12px;padding:1.2rem;text-align:center;border:1px solid #2d4070;margin-bottom:1rem;}
.metric-value{font-size:2.2rem;font-weight:700;color:#f0c040;}
.metric-label{font-size:.85rem;color:#8aa0cc;}
h1,h2,h3{color:#e0e8ff!important;}
.stButton>button{background:linear-gradient(135deg,#2d5af0,#1a3acc);color:#fff;border:none;border-radius:8px;font-weight:600;width:100%;}
.stTextInput>div>div>input{background:#243560!important;color:#e0e8ff!important;border:1px solid #2d4070!important;border-radius:8px!important;}
</style>
""", unsafe_allow_html=True)

DATA_FILE   = "students.json"
ATTEND_FILE = "attendance.json"

def load_students():
    return json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else {}

def save_students(d):
    json.dump(d, open(DATA_FILE,"w"), indent=2)

def load_attendance():
    return json.load(open(ATTEND_FILE)) if os.path.exists(ATTEND_FILE) else {}

def save_attendance(d):
    json.dump(d, open(ATTEND_FILE,"w"), indent=2)

def mark_attendance(roll):
    roll = roll.strip()
    students = load_students()
    if roll not in students:
        return False, f"❌ Roll No '{roll}' not found!"
    att = load_attendance()
    today = str(date.today())
    att.setdefault(today, {})
    if roll in att[today]:
        return False, f"⚠️ Already marked: {students[roll]['name']}"
    att[today][roll] = {"name":students[roll]["name"],"dept":students[roll]["dept"],
                        "time":datetime.now().strftime("%H:%M:%S")}
    save_attendance(att)
    return True, f"✅ Present: {students[roll]['name']} ({roll})"

def make_qr(roll):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(roll); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf,"PNG"); return buf.getvalue()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0'>
      <div style='font-size:3rem'>🎓</div>
      <div style='font-size:1.2rem;font-weight:700;color:#f0c040'>Auxilium College</div>
      <div style='font-size:.8rem;color:#8aa0cc'>QR Attendance System</div>
    </div>
    <hr style='border-color:#2d4070;margin:.5rem 0 1.5rem'>
    """, unsafe_allow_html=True)
    page = st.radio("Nav", [
        "➕ Add Student","👥 Students List","📷 QR Scanner",
        "📊 Today Summary","📋 Attendance Report"
    ], label_visibility="collapsed")
    st.markdown(f"<div style='text-align:center;color:#8aa0cc;font-size:.8rem;margin-top:2rem'>📅 {date.today()}</div>", unsafe_allow_html=True)

# ── Add Student ────────────────────────────────────────────────────────────────
if page == "➕ Add Student":
    st.title("➕ Add Student")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Student Details")
        roll = st.text_input("Roll Number", placeholder="e.g. BCA1")
        name = st.text_input("Full Name", placeholder="e.g. Hema Priya")
        dept = st.selectbox("Department", ["BCA","BBA","Computer Science","Mathematics",
                                            "Physics","Chemistry","Commerce","English","History","Economics"])
        year = st.selectbox("Year", ["1st Year","2nd Year","3rd Year"])
        if st.button("💾 Add Student"):
            if not roll or not name: st.error("Fill Roll Number & Name!")
            else:
                s = load_students()
                if roll in s: st.error(f"{roll} already exists!")
                else:
                    s[roll]={"name":name,"dept":dept,"year":year,"added_on":str(date.today())}
                    save_students(s); st.success(f"✅ {name} added!"); st.balloons()
    with c2:
        st.subheader("🔲 Generate QR Code")
        qr_roll = st.text_input("Roll No for QR", placeholder="e.g. BCA1", key="qrgen")
        if st.button("Generate QR"):
            s = load_students()
            if qr_roll in s:
                qb = make_qr(qr_roll)
                st.image(qb, caption=f"{s[qr_roll]['name']} — {qr_roll}", width=260)
                st.download_button("⬇️ Download QR", qb, f"QR_{qr_roll}.png","image/png")
            else: st.error("Roll No not found!")

# ── Students List ──────────────────────────────────────────────────────────────
elif page == "👥 Students List":
    st.title("👥 Students List")
    st.markdown("---")
    s = load_students()
    if not s: st.info("No students yet.")
    else:
        ta = load_attendance().get(str(date.today()), {})
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(s)}</div><div class="metric-label">Total</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(ta)}</div><div class="metric-label">Present Today</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(s)-len(ta)}</div><div class="metric-label">Absent Today</div></div>',unsafe_allow_html=True)
        search = st.text_input("🔍 Search")
        rows=[{"Roll No":r,"Name":i["name"],"Dept":i["dept"],"Year":i["year"],
               "Today":"✅" if r in ta else "❌"} for r,i in s.items()
              if not search or search.lower() in r.lower() or search.lower() in i["name"].lower()]
        if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        st.markdown("---")
        dr=st.text_input("Roll No to delete")
        if st.button("🗑️ Delete"):
            if dr in s: del s[dr]; save_students(s); st.success("Deleted!"); st.rerun()
            else: st.error("Not found!")

# ── QR Scanner ─────────────────────────────────────────────────────────────────
elif page == "📷 QR Scanner":
    st.title("📷 QR Scanner")
    st.markdown("---")

    if "scanner_locked" not in st.session_state:
        st.session_state.scanner_locked = False
    if st.button("🔓 Unlock Scanner" if st.session_state.scanner_locked else "🔒 Lock Scanner"):
        st.session_state.scanner_locked = not st.session_state.scanner_locked
        st.rerun()

    if st.session_state.scanner_locked:
        st.warning("🔒 Scanner is locked.")
    else:
        st.info("📸 QR scan பண்ணினா Roll No auto-fill ஆகும் — Mark Present click பண்ணுங்க!")

        # ── Scanner + auto-fill using Streamlit's websocket via postMessage ──
        # The scanner detects QR → stores in sessionStorage → Streamlit polls it
        scanned_roll = components.html("""
<!DOCTYPE html><html><head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html5-qrcode/2.3.8/html5-qrcode.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#1a2a4a;font-family:Arial,sans-serif;color:#e0e8ff;padding:1rem}
#reader{max-width:360px;margin:0 auto;border-radius:10px;overflow:hidden}
#status{margin:.8rem 0;padding:.8rem;border-radius:8px;background:#243560;color:#8aa0cc;text-align:center}
#status.ok{background:#1a3a2a;color:#2ecc71;border-left:4px solid #2ecc71}
#status.scan{background:#1a2040;color:#f0c040;border-left:4px solid #f0c040}
#roll-display{background:#243560;border-radius:8px;padding:.8rem;margin:.5rem 0;text-align:center;font-size:1.2rem;font-weight:700;color:#f0c040;display:none}
.btn{display:inline-block;margin:.4rem;padding:.5rem 1.5rem;background:linear-gradient(135deg,#2d5af0,#1a3acc);color:#fff;border:none;border-radius:8px;font-size:.95rem;cursor:pointer;font-weight:600}
.btn.green{background:linear-gradient(135deg,#27ae60,#1e8449)}
#log{margin-top:.5rem}
.li{background:#1a3a2a;border-radius:6px;padding:.3rem .8rem;margin:.2rem 0;color:#2ecc71;font-size:.85rem}
</style></head><body>
<div id="reader"></div>
<div id="status" class="scan">📷 Camera starting...</div>
<div id="roll-display"></div>
<div style="text-align:center">
  <button class="btn" id="stop-btn" onclick="toggle()">⏹ Stop</button>
</div>
<div id="log"></div>
<script>
let qr=null,on=false,last="",lastT=0,log=[];
const setS=(m,c)=>{const e=document.getElementById("status");e.className=c||"";e.innerText=m};

function onScan(text){
  const now=Date.now();
  if(text===last&&now-lastT<4000)return;
  last=text;lastT=now;
  const roll=text.trim();
  
  // Show scanned roll prominently
  const rd=document.getElementById("roll-display");
  rd.style.display="block";
  rd.innerText="📋 Scanned: "+roll;
  setS("✅ Scanned: "+roll+" — Click Mark Present below","ok");
  
  // Add to log
  log.unshift(roll);
  if(log.length>5)log.pop();
  document.getElementById("log").innerHTML=
    "<div style='color:#8aa0cc;font-size:.8rem;margin:.4rem 0'>Recent scans:</div>"+
    log.map(x=>`<div class='li'>✅ ${x}</div>`).join("");
  
  // Send to Streamlit via postMessage (Streamlit component protocol)
  window.parent.postMessage({
    isStreamlitMessage: true,
    type: "streamlit:componentValue", 
    value: roll
  }, "*");
}

function start(){
  qr=new Html5Qrcode("reader");
  qr.start({facingMode:"environment"},{fps:10,qrbox:{width:230,height:230}},onScan,()=>{})
  .then(()=>{setS("✅ Camera On — QR காட்டுங்க","scan");document.getElementById("stop-btn").innerText="⏹ Stop";on=true})
  .catch(e=>{setS("❌ Camera error: "+e,"")})
}
function stop(){
  qr&&qr.stop().then(()=>{
    setS("📷 Camera stopped","");
    document.getElementById("stop-btn").innerText="▶ Start";on=false;
  })
}
function toggle(){on?stop():start()}
start();
</script></body></html>
""", height=520)

        # ── Mark attendance form ───────────────────────────────────────────────
        st.markdown("---")

        # Initialize session roll
        if "current_roll" not in st.session_state:
            st.session_state.current_roll = ""

        col1, col2 = st.columns([3,1])
        with col1:
            roll_input = st.text_input(
                "Roll Number",
                value=st.session_state.current_roll,
                placeholder="QR scan பண்ணினா இங்க வரும் — or type manually",
                key="roll_box"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            mark_btn = st.button("✅ Mark Present", use_container_width=True)

        if mark_btn and roll_input:
            ok, msg = mark_attendance(roll_input.strip())
            if ok:
                st.success(f"🎉 {msg}")
                st.session_state.current_roll = ""
                st.balloons()
                st.rerun()
            else:
                st.error(msg)

    # Today's list
    today_att = load_attendance().get(str(date.today()), {})
    if today_att:
        st.markdown("---")
        st.subheader(f"✅ Present Today — {len(today_att)} students")
        rows=[{"Roll No":r,"Name":v["name"],"Dept":v["dept"],"Time":v["time"]} for r,v in today_att.items()]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

# ── Today Summary ──────────────────────────────────────────────────────────────
elif page == "📊 Today Summary":
    st.title("📊 Today Summary")
    st.caption(date.today().strftime('%A, %d %B %Y'))
    st.markdown("---")
    s=load_students(); ta=load_attendance().get(str(date.today()),{})
    total=len(s); present=len(ta); absent=total-present
    pct=round(present/total*100,1) if total else 0
    c1,c2,c3,c4=st.columns(4)
    for col,(v,l,color) in zip([c1,c2,c3,c4],[(total,"Total","#f0c040"),(present,"Present","#2ecc71"),(absent,"Absent","#e74c3c"),(f"{pct}%","Att %","#2d5af0")]):
        with col: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{v}</div><div class="metric-label">{l}</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.subheader(f"✅ Present ({present})")
        if ta: st.dataframe(pd.DataFrame([{"Roll":r,"Name":v["name"],"Time":v["time"]} for r,v in ta.items()]),use_container_width=True,hide_index=True)
        else: st.info("No attendance yet.")
    with c2:
        st.subheader(f"❌ Absent ({absent})")
        ar=[{"Roll":r,"Name":i["name"]} for r,i in s.items() if r not in ta]
        if ar: st.dataframe(pd.DataFrame(ar),use_container_width=True,hide_index=True)
        else: st.success("All present! 🎉")
    st.markdown("---")
    with st.form("mf"):
        m=st.text_input("Manual Roll No",placeholder="e.g. BCA1")
        if st.form_submit_button("Mark Present"):
            ok,msg=mark_attendance(m)
            if ok: st.success(msg); st.rerun()
            else: st.error(msg)

# ── Attendance Report ──────────────────────────────────────────────────────────
elif page == "📋 Attendance Report":
    st.title("📋 Attendance Report")
    st.markdown("---")
    s=load_students(); att=load_attendance()
    if not att: st.info("No records yet.")
    else:
        sel=st.selectbox("Date",sorted(att.keys(),reverse=True))
        if sel:
            day=att[sel]; total=len(s); present=len(day)
            c1,c2,c3=st.columns(3)
            with c1: st.metric("Present",present)
            with c2: st.metric("Absent",total-present)
            with c3: st.metric("Att %",f"{round(present/total*100,1) if total else 0}%")
            rows=[{"Roll No":r,"Name":i["name"],"Dept":i["dept"],
                   "Status":"✅ Present" if r in day else "❌ Absent",
                   "Time":day[r]["time"] if r in day else "-"} for r,i in s.items()]
            df=pd.DataFrame(rows)
            st.dataframe(df,use_container_width=True,hide_index=True)
            st.download_button("⬇️ CSV",df.to_csv(index=False),f"att_{sel}.csv","text/csv")
        st.markdown("---")
        st.subheader("📈 All-time")
        rows=[{"Roll No":r,"Name":i["name"],"Present":sum(1 for d in att.values() if r in d),
               "Total":len(att),"Att %":f"{round(sum(1 for d in att.values() if r in d)/len(att)*100,1)}%"} for r,i in s.items()]
        if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
