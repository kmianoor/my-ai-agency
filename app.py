import os
import json
import time
import traceback
import pandas as pd
import streamlit as st
from PIL import Image
from io import BytesIO
from google import genai
from google.genai import types

# ==========================================
# PAGE CONFIG & AGENCY STYLING
# ==========================================
st.set_page_config(page_title="2026 Full AI Agency", page_icon="🏢", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #090d16; color: #ffffff; }
    .agent-card {
        background-color: #131926;
        border: 2px solid #232d42;
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        transition: all 0.3s ease;
        min-height: 155px;
    }
    .agent-active {
        background-color: #162638;
        border: 2px solid #00ffcc;
        box-shadow: 0 0 18px rgba(0, 255, 204, 0.6);
        transform: scale(1.06);
    }
    .agent-verify {
        background-color: #2b1d38;
        border: 2px solid #ffaa00;
        box-shadow: 0 0 18px rgba(255, 170, 0, 0.6);
        transform: scale(1.06);
    }
    .agent-avatar { font-size: 36px; margin-bottom: 4px; }
    .agent-name { font-weight: bold; font-size: 14px; color: #ffffff; }
    .agent-role { font-size: 11px; color: #8b9bb4; }
    .agent-status-idle { color: #6c7a96; font-size: 11px; margin-top: 6px; }
    .agent-status-work { color: #00ffcc; font-weight: bold; font-size: 11px; margin-top: 6px; animation: pulse 1.2s infinite; }
    .agent-status-verify { color: #ffaa00; font-weight: bold; font-size: 11px; margin-top: 6px; animation: pulse 1.2s infinite; }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

MEMORY_FILE = "agency_memory.json"
WORK_DIR = os.path.join(os.getcwd(), "AI_Agency_Workspace")
os.makedirs(WORK_DIR, exist_ok=True)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"rules": []}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==========================================
# SIDEBAR: CONTROL PANEL & MEMORY
# ==========================================
with st.sidebar:
    st.title("🏢 Agency Control")
    api_key = st.text_input("🔑 Google Gemini API Key:", type="password")
    
    st.divider()
    custom_folder = st.text_input("📁 Workspace Folder:", value=WORK_DIR)
    if os.path.exists(custom_folder):
        files_in_folder = [f for f in os.listdir(custom_folder) if not f.startswith("~$")]
        st.success(f"Folder Active ({len(files_in_folder)} files)")
        with st.expander("📂 Folder Files"):
            for f in files_in_folder:
                st.write(f"📄 {f}")

    st.divider()
    st.subheader("🧠 Agency Memory")
    mem = load_memory()
    if mem["rules"]:
        for idx, r in enumerate(mem["rules"]):
            st.info(f"{idx+1}. {r}")
        if st.button("🗑️ Memory Saaf Karein"):
            save_memory({"rules": []})
            st.rerun()
    save_to_mem = st.checkbox("💾 Is kaam ko hamesha ke liye Memory mein save karein")

# ==========================================
# MAIN SCREEN: THE 7-AGENT PIPELINE
# ==========================================
st.title("🏢 2026 End-to-End Autonomous AI Agency")
st.caption("Planner • Inspector • Specialists • Quality Verifier (Full Pipeline)")

if not api_key:
    st.warning("👈 Shuru karne ke liye baayein taraf (Sidebar) mein apni Gemini API Key paste karein.")
    st.stop()

client = genai.Client(api_key=api_key)
office_display = st.empty()

def render_agency(active_agent="NONE", status_msg="Intezar..."):
    agents = [
        {"id": "BOSS", "avatar": "🧑‍💼", "name": "Mr. Boss", "role": "CEO & Planner"},
        {"id": "INSPECTOR", "avatar": "🔍", "name": "Maya", "role": "Data Inspector"},
        {"id": "EXCEL", "avatar": "📊", "name": "Sara", "role": "Excel Specialist"},
        {"id": "DESIGN", "avatar": "🎨", "name": "Leo", "role": "Graphic Designer"},
        {"id": "YOUTUBE", "avatar": "🎬", "name": "Zain", "role": "YouTube Director"},
        {"id": "CODING", "avatar": "👨‍💻", "name": "Max", "role": "Software Coder"},
        {"id": "VERIFIER", "avatar": "🕵️‍♀️", "name": "Ayesha", "role": "Quality Verifier"},
    ]
    
    with office_display.container():
        cols = st.columns(7)
        for idx, ag in enumerate(agents):
            is_active = (ag["id"] == active_agent)
            if is_active and ag["id"] == "VERIFIER":
                card_class = "agent-card agent-verify"
                status_class = "agent-status-verify"
            elif is_active:
                card_class = "agent-card agent-active"
                status_class = "agent-status-work"
            else:
                card_class = "agent-card"
                status_class = "agent-status-idle"
                
            current_text = f"⚡ {status_msg}" if is_active else "💤 Ready"
            
            cols[idx].markdown(f"""
            <div class="{card_class}">
                <div class="agent-avatar">{ag['avatar']}</div>
                <div class="agent-name">{ag['name']}</div>
                <div class="agent-role">{ag['role']}</div>
                <div class="{status_class}">{current_text}</div>
            </div>
            """, unsafe_allow_html=True)

render_agency("NONE")
st.divider()

# File Uploader
uploaded_files = st.file_uploader("📤 Files yahan drop karein:", type=["xlsx", "csv"], accept_multiple_files=True)
if uploaded_files:
    for uf in uploaded_files:
        with open(os.path.join(custom_folder, uf.name), "wb") as f:
            f.write(uf.getbuffer())
    st.toast("Files workspace mein aa gayi hain!", icon="✅")

user_task = st.chat_input("Apna poora project ya hukum likhein...")

if user_task:
    with st.chat_message("user"):
        st.write(user_task)

    if save_to_mem:
        mem["rules"].append(user_task)
        save_memory(mem)

    with st.chat_message("assistant"):
        log = st.container()
        
        # STAGE 1: MR. BOSS (PLANNING)
        render_agency("BOSS", "Project Plan bana raha hoon...")
        log.write("🧑‍💼 **Mr. Boss (CEO):** Hukum mil gaya! Main is kaam ka step-by-step plan bana kar team ko assign kar raha hoon...")
        time.sleep(1)

        plan_prompt = f"""
        User ka kaam: "{user_task}"
        Faisla karo ke main department kaunsa hai (EXCEL, DESIGN, YOUTUBE, ya CODING) aur 2 lines mein is ka plan likho.
        Format:
        DEPT: [EXCEL/DESIGN/YOUTUBE/CODING]
        PLAN: [Short plan in Urdu/English]
        """
        plan_res = client.models.generate_content(model="gemini-2.5-flash", contents=plan_prompt).text.strip()
        dept = "EXCEL" if "EXCEL" in plan_res.upper() else ("DESIGN" if "DESIGN" in plan_res.upper() else ("YOUTUBE" if "YOUTUBE" in plan_res.upper() else "CODING"))
        log.info(f"📋 **Project Plan:**\n{plan_res}")

        # STAGE 2: EXCEL DEPARTMENT
        if dept == "EXCEL":
            render_agency("INSPECTOR", "Files aur data scan kar rahi hoon...")
            log.write("🔍 **Maya (Inspector):** Main folder mein mojood tamam Excel files aur un ke columns ki gehrai se jaanch kar rahi hoon...")
            time.sleep(1)
            
            excel_files = [os.path.join(custom_folder, f) for f in os.listdir(custom_folder) if f.endswith((".xlsx", ".csv")) and not f.startswith("DONE_")]
            if not excel_files:
                log.error("🔍 **Maya:** Boss, folder mein koi Excel file nahi mili! Pehle file upload karein.")
                render_agency("NONE")
                st.stop()

            files_info = ""
            for fp in excel_files:
                try:
                    df = pd.read_excel(fp) if fp.endswith(".xlsx") else pd.read_csv(fp)
                    files_info += f"\nFile: '{fp}' | Rows: {len(df)} | Columns: {list(df.columns)}\nSample:\n{df.head(3).to_string()}\n"
                except Exception:
                    pass
            log.write(f"🔍 **Maya:** Jaanch mukammal! Kul {len(excel_files)} files mili hain. Report **Sara** ko bhej di hai.")

            mem_context = "\n".join(mem["rules"])
            feedback = ""
            
            for cycle in range(1, 4):
                render_agency("EXCEL", f"Kaam kar rahi hoon (Round {cycle})...")
                log.write(f"📊 **Sara (Excel Specialist):** Round {cycle} — Main calculations, formatting aur charts par kaam kar rahi hoon...")
                
                code_prompt = f"""
                Tum Sara ho, aik expert Python Excel Developer.
                Folder: r"{custom_folder}"
                Files Info: {files_info}
                Memory Rules: {mem_context}
                User Instruction: "{user_task}"
                Verifier Feedback: "{feedback}"

                Rules:
                1. Pandas aur openpyxl (colors, borders, auto-fit width, charts) use karo.
                2. Output file ko '{custom_folder}' mein 'DONE_' prefix ke sath save karo.
                3. Sirf pure Python code do, koi markdown nahi.
                """
                
                code = client.models.generate_content(model="gemini-2.5-flash", contents=code_prompt).text.strip().replace("```python", "").replace("```", "")
                
                try:
                    exec(code, globals())
                except Exception:
                    err = traceback.format_exc()
                    render_agency("CODING", "Error fix kar raha hoon...")
                    log.warning("👨‍💻 **Max (Coder):** Code mein technical error aaya hai, main abhi theek kar ke Sara ko deta hoon!")
                    fix_prompt = f"Error:\n{err}\nCode:\n{code}\nIsay theek kar ke pure Python code do."
