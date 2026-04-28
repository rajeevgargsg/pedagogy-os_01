import streamlit as st
from groq import Groq
import json
import time
import re
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PedagogyOS — Autonomous Curriculum Engine (Groq)",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:        #080c10;
    --bg2:       #0d1219;
    --bg3:       #131b24;
    --border:    #1e2d3d;
    --teal:      #00d4aa;
    --teal2:     #00a882;
    --amber:     #f59e0b;
    --rose:      #f43f5e;
    --blue:      #3b82f6;
    --purple:    #8b5cf6;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --card:      rgba(13,18,25,0.95);
  }
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .stApp { background: var(--bg); color: var(--text); }
  .stApp > header { background: transparent !important; }
  section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border);
  }
  section[data-testid="stSidebar"] * { color: var(--text) !important; }

  /* ── Hero ── */
  .hero {
    background: linear-gradient(135deg, #050a10 0%, #0a1628 40%, #051219 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 40px 48px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,212,170,0.08) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero::after {
    content: '';
    position: absolute; bottom: -80px; left: 20%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-label {
    font-family: 'Space Mono', monospace;
    font-size: 11px; letter-spacing: 3px;
    color: var(--teal); text-transform: uppercase;
    margin-bottom: 12px;
  }
  .hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(28px, 4vw, 46px);
    font-weight: 800; line-height: 1.15;
    color: #fff; margin: 0 0 14px;
  }
  .hero h1 span { color: var(--teal); }
  .hero-sub {
    color: var(--muted); font-size: 15px;
    max-width: 580px; line-height: 1.65;
  }

  /* ── Agent Cards ── */
  .agent-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 16px;
    position: relative;
    transition: border-color 0.3s;
  }
  .agent-card.active { border-color: var(--teal); }
  .agent-card.done   { border-color: rgba(0,212,170,0.3); }
  .agent-card.failed { border-color: var(--rose); }
  .agent-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 8px;
  }
  .agent-icon {
    width: 36px; height: 36px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
  }
  .icon-architect { background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.3); }
  .icon-content   { background: rgba(59,130,246,0.15);  border: 1px solid rgba(59,130,246,0.3); }
  .icon-student   { background: rgba(245,158,11,0.15);  border: 1px solid rgba(245,158,11,0.3); }
  .icon-loop      { background: rgba(244,63,94,0.15);   border: 1px solid rgba(244,63,94,0.3); }
  .agent-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 14px; color: #fff;
  }
  .agent-role {
    font-family: 'Space Mono', monospace;
    font-size: 10px; letter-spacing: 1.5px;
    color: var(--muted); text-transform: uppercase;
  }
  .status-badge {
    margin-left: auto;
    font-family: 'Space Mono', monospace;
    font-size: 10px; letter-spacing: 1px;
    padding: 3px 8px; border-radius: 20px;
    text-transform: uppercase;
  }
  .badge-idle    { background: rgba(100,116,139,0.15); color: var(--muted); border: 1px solid var(--border); }
  .badge-running { background: rgba(0,212,170,0.12);   color: var(--teal);  border: 1px solid rgba(0,212,170,0.3); }
  .badge-done    { background: rgba(0,212,170,0.08);   color: var(--teal2); border: 1px solid rgba(0,212,170,0.2); }
  .badge-failed  { background: rgba(244,63,94,0.12);   color: var(--rose);  border: 1px solid rgba(244,63,94,0.3); }
  .agent-desc { font-size: 13px; color: var(--muted); line-height: 1.6; }

  /* ── Pipeline Arrow ── */
  .pipeline-arrow {
    text-align: center; color: var(--border);
    font-size: 20px; margin: 4px 0;
  }

  /* ── Lesson Content ── */
  .lesson-section {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 14px;
  }
  .lesson-event-tag {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 10px; letter-spacing: 2px;
    color: var(--teal); text-transform: uppercase;
    background: rgba(0,212,170,0.08);
    border: 1px solid rgba(0,212,170,0.2);
    padding: 2px 8px; border-radius: 4px;
    margin-bottom: 10px;
  }
  .lesson-title {
    font-family: 'Syne', sans-serif;
    font-size: 18px; font-weight: 700;
    color: #fff; margin-bottom: 10px;
  }
  .lesson-body { font-size: 14px; color: #b0bec5; line-height: 1.75; }
  .code-block {
    background: #0a0f15;
    border: 1px solid var(--border);
    border-left: 3px solid var(--teal);
    border-radius: 6px;
    padding: 14px 16px;
    font-family: 'Space Mono', monospace;
    font-size: 12px; color: #a5d6a7;
    overflow-x: auto; margin: 12px 0;
    white-space: pre-wrap;
  }

  /* ── Assessment ── */
  .quiz-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 22px; margin-bottom: 12px;
  }
  .quiz-number {
    font-family: 'Space Mono', monospace;
    font-size: 11px; color: var(--teal);
    margin-bottom: 6px;
  }
  .quiz-q { font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 12px; }

  /* ── Student Result ── */
  .result-pass {
    background: rgba(0,212,170,0.06);
    border: 1px solid rgba(0,212,170,0.25);
    border-radius: 10px; padding: 16px 20px;
    margin-bottom: 12px;
  }
  .result-fail {
    background: rgba(244,63,94,0.06);
    border: 1px solid rgba(244,63,94,0.25);
    border-radius: 10px; padding: 16px 20px;
    margin-bottom: 12px;
  }
  .result-label {
    font-family: 'Space Mono', monospace;
    font-size: 11px; letter-spacing: 2px;
    text-transform: uppercase; margin-bottom: 8px;
  }

  /* ── Failure Log ── */
  .failure-log {
    background: rgba(244,63,94,0.04);
    border: 1px solid rgba(244,63,94,0.2);
    border-radius: 8px; padding: 14px 18px;
    font-family: 'Space Mono', monospace;
    font-size: 11px; color: #fca5a5;
    line-height: 1.8; margin: 10px 0;
  }

  /* ── Progress Bar ── */
  .progress-track {
    background: var(--border); border-radius: 4px; height: 4px;
    margin: 10px 0; overflow: hidden;
  }
  .progress-fill {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, var(--teal), var(--blue));
    transition: width 0.4s ease;
  }

  /* ── Metric Tiles ── */
  .metric-row { display: flex; gap: 12px; margin-bottom: 24px; }
  .metric-tile {
    flex: 1; background: var(--bg2);
    border: 1px solid var(--border); border-radius: 10px;
    padding: 16px 18px;
  }
  .metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 28px; font-weight: 800; color: #fff;
    line-height: 1;
  }
  .metric-val.teal  { color: var(--teal); }
  .metric-val.amber { color: var(--amber); }
  .metric-val.rose  { color: var(--rose); }
  .metric-val.blue  { color: var(--blue); }
  .metric-lbl {
    font-family: 'Space Mono', monospace;
    font-size: 10px; color: var(--muted);
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-top: 6px;
  }

  /* ── Streamlit overrides ── */
  .stButton > button {
    background: linear-gradient(135deg, var(--teal), var(--teal2)) !important;
    color: #000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    border: none !important; border-radius: 8px !important;
    padding: 10px 28px !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.9; transform: translateY(-1px); }
  div[data-baseweb="select"] > div,
  div[data-baseweb="textarea"] > div > div,
  div[data-baseweb="input"] > div {
    background: var(--bg3) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
  }
  textarea, input[type="text"], input[type="password"] {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
  }
  .stTextArea textarea { font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; }
  .stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    padding: 4px !important; gap: 4px !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important; letter-spacing: 1px !important;
    border-radius: 8px !important;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(0,212,170,0.12) !important;
    color: var(--teal) !important;
  }
  .stExpander { border: 1px solid var(--border) !important; border-radius: 10px !important; background: var(--bg2) !important; }
  .stMarkdown h2 { font-family: 'Syne', sans-serif !important; color: #fff !important; }
  .stMarkdown h3 { font-family: 'Syne', sans-serif !important; color: #e2e8f0 !important; }
  hr { border-color: var(--border) !important; }
  .stSpinner > div { color: var(--teal) !important; }
  .stInfo { background: rgba(0,212,170,0.06) !important; border-color: rgba(0,212,170,0.3) !important; color: var(--text) !important; }
  .stSuccess { background: rgba(0,212,170,0.08) !important; border-color: rgba(0,212,170,0.4) !important; }
  .stWarning { background: rgba(245,158,11,0.08) !important; border-color: rgba(245,158,11,0.4) !important; }
  .stError { background: rgba(244,63,94,0.08) !important; border-color: rgba(244,63,94,0.4) !important; }
  div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
  .stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label,
  .stRadio label, .stCheckbox label {
    color: var(--muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
  }
  .sidebar-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 18px; color: #fff;
    padding: 12px 0 4px;
  }
  .sidebar-section {
    font-family: 'Space Mono', monospace;
    font-size: 10px; letter-spacing: 2px;
    color: var(--teal); text-transform: uppercase;
    margin: 20px 0 10px; border-top: 1px solid var(--border);
    padding-top: 14px;
  }
</style>
""", unsafe_allow_html=True)

# ─── Session State ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "api_key": "",
        "groq_model": "llama-3.3-70b-versatile",
        "raw_doc": "",
        "framework": "gagne",
        "student_persona": "novice",
        "architect_output": None,
        "content_output": None,
        "student_output": None,
        "iteration": 0,
        "max_iterations": 3,
        "pipeline_done": False,
        "pipeline_running": False,
        "agent_states": {"architect": "idle", "content": "idle", "student": "idle", "loop": "idle"},
        "lesson_tabs": [],
        "assessment_answers": {},
        "show_rewrite": False,
        "rewrite_logs": [],
        "final_score": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
# Auto-load from Streamlit secrets if available
if "GROQ_API_KEY" in st.secrets and not st.session_state.api_key:
    st.session_state.api_key = st.secrets["GROQ_API_KEY"]
# ─── API helpers ───────────────────────────────────────────────────────────────
def get_client():
    key = st.session_state.api_key.strip()
    if not key:
        return None
    return Groq(api_key=key)

def call_claude(client, system_prompt: str, user_prompt: str, max_tokens=4096) -> str:
    """Groq drop-in: same signature, uses OpenAI-compatible chat completions."""
    resp = client.chat.completions.create(
        model=st.session_state.get("groq_model", "llama-3.3-70b-versatile"),
        max_tokens=max_tokens,
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content

def safe_json(text: str):
    """Extract first JSON object or array from text."""
    text = text.strip()
    # Try to strip markdown code fences
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```\s*$', '', text, flags=re.MULTILINE)
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return None

# ─── Agent Prompts ─────────────────────────────────────────────────────────────

ARCHITECT_SYSTEM = """You are the Architect Agent — a master instructional designer.
Your role: Analyse raw technical documentation and produce a strict pedagogical outline.

You MUST return valid JSON only — no prose before or after. Use this exact schema:

{
  "framework": "<gagne|merrill>",
  "title": "<lesson title>",
  "topic_summary": "<2-sentence summary of what the documentation covers>",
  "learning_objectives": ["<obj 1>", "<obj 2>", "<obj 3>"],
  "difficulty": "<beginner|intermediate|advanced>",
  "estimated_minutes": <integer>,
  "sections": [
    {
      "event_id": <integer 1-9 for gagne OR "activate|demonstrate|apply|integrate" for merrill>,
      "event_name": "<event label>",
      "purpose": "<why this event matters>",
      "content_cues": "<what to cover here>",
      "duration_minutes": <integer>
    }
  ],
  "key_concepts": ["<concept>"],
  "prerequisite_knowledge": ["<prereq>"],
  "assessment_blueprint": {
    "quiz_count": <integer 3-5>,
    "exercise_count": <integer 1-3>,
    "mastery_threshold": <0.0-1.0>
  }
}"""

def build_architect_prompt(doc: str, framework: str) -> str:
    fw = "Gagné's Nine Events of Instruction (9 events: Gain Attention, Inform Objectives, Stimulate Recall, Present Content, Provide Guidance, Elicit Performance, Provide Feedback, Assess Performance, Enhance Retention)" \
         if framework == "gagne" else \
         "Merrill's First Principles (4 phases: Activation of prior knowledge, Demonstration of skills, Application of learning, Integration into real world — all centred on an authentic Problem-centred task)"
    return f"""Map the following technical documentation to {fw}.

RAW DOCUMENTATION:
---
{doc[:6000]}
---

Produce the JSON outline now."""


CONTENT_SYSTEM = """You are the Content Agent — a brilliant technical writer and educator.
Given an instructional outline (JSON), generate full lesson material.

Return ONLY valid JSON with this schema:

{{
  "lesson_title": "<title>",
  "sections": [
    {{
      "event_id": "<same as architect>",
      "event_name": "<same as architect>",
      "content": "<rich markdown-flavoured explanatory text, 150-300 words>",
      "code_example": "<optional code snippet as a string, or null>",
      "visual_cue": "<description of a diagram/concept map idea, or null>"
    }}
  ],
  "quizzes": [
    {{
      "id": <integer>,
      "question": "<question text>",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct": "<A|B|C|D>",
      "explanation": "<why this answer is correct>"
    }}
  ],
  "exercises": [
    {{
      "id": <integer>,
      "title": "<exercise title>",
      "description": "<task description>",
      "starter_code": "<starter code or null>",
      "expected_output": "<what a correct solution does>",
      "hints": ["<hint 1>", "<hint 2>"]
    }}
  ]
}}"""

def build_content_prompt(outline: dict, raw_doc: str, failure_log: str = None) -> str:
    base = f"""ARCHITECT OUTLINE:
{json.dumps(outline, indent=2)}

ORIGINAL DOCUMENTATION (for reference):
---
{raw_doc[:4000]}
---
"""
    if failure_log:
        base += f"""
STUDENT FAILURE LOG — you MUST address these gaps in your revised content:
{failure_log}

Rewrite confusing sections, add non-examples (what NOT to do), and provide extra scaffolding.
"""
    base += "\nGenerate the full lesson content now."
    return base


STUDENT_SYSTEM = """You are the Simulated Student Agent — an objective validator.
Your role: attempt the exercises and quizzes in a lesson as a specific student persona.
Return ONLY valid JSON:

{{
  "persona": "<novice|intermediate|advanced>",
  "quiz_attempts": [
    {{
      "id": <integer>,
      "selected": "<A|B|C|D>",
      "correct": <true|false>,
      "reasoning": "<why you chose this>"
    }}
  ],
  "exercise_attempts": [
    {{
      "id": <integer>,
      "attempt_code": "<your solution code or prose>",
      "passed": <true|false>,
      "confidence": <0.0-1.0>,
      "confusion_points": ["<what was unclear>"]
    }}
  ],
  "overall_score": <0.0-1.0>,
  "passed": <true|false>,
  "failure_log": "<detailed log of what was unclear, ambiguous or missing — null if passed>",
  "gaps_identified": ["<learning gap 1>", "<learning gap 2>"]
}}"""

def build_student_prompt(lesson: dict, persona: str, mastery: float) -> str:
    return f"""STUDENT PERSONA: {persona}
MASTERY THRESHOLD: {mastery} (you pass only if overall_score >= {mastery})

LESSON TO ATTEMPT:
{json.dumps(lesson, indent=2)[:6000]}

Attempt all quizzes and exercises honestly as a {persona} student. 
Identify genuine confusion points. Be critical — find real weaknesses in the lesson."""

# ─── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(client, doc: str, framework: str, persona: str, progress_col):
    """Run the full multi-agent pipeline. Updates session state throughout."""
    ss = st.session_state
    ss["pipeline_running"] = True
    ss["iteration"] = 0
    ss["rewrite_logs"] = []
    failure_log = None

    with progress_col:
        prog_bar = st.progress(0, text="Initialising pipeline…")

        # ── ARCHITECT ────────────────────────────────────────────────────────
        ss["agent_states"]["architect"] = "running"
        prog_bar.progress(10, text="🔭 Architect Agent: Mapping documentation to pedagogical framework…")
        st.rerun() if False else None  # trigger UI update trick (avoid in loops)

        try:
            arch_raw = call_claude(
                client,
                ARCHITECT_SYSTEM,
                build_architect_prompt(doc, framework),
                max_tokens=2048
            )
            arch = safe_json(arch_raw)
            if not arch:
                arch = {"title": "Lesson", "framework": framework, "sections": [],
                        "learning_objectives": [], "key_concepts": [],
                        "prerequisite_knowledge": [], "estimated_minutes": 30,
                        "difficulty": "intermediate",
                        "assessment_blueprint": {"quiz_count": 4, "exercise_count": 2, "mastery_threshold": 0.75},
                        "topic_summary": arch_raw[:300], "raw": arch_raw}
            ss["architect_output"] = arch
            ss["agent_states"]["architect"] = "done"
        except Exception as e:
            ss["agent_states"]["architect"] = "failed"
            prog_bar.progress(100, text=f"❌ Architect failed: {e}")
            ss["pipeline_running"] = False
            return

        prog_bar.progress(33, text="✅ Architect done — blueprint ready. Content Agent taking over…")
        time.sleep(0.3)

        # ── CONTENT (with possible rewrites) ────────────────────────────────
        for iteration in range(ss["max_iterations"]):
            ss["iteration"] = iteration
            ss["agent_states"]["content"] = "running"
            frac = 33 + int(22 * (iteration / ss["max_iterations"]))
            prog_bar.progress(frac, text=f"✍️  Content Agent: {'Generating' if iteration==0 else 'Rewriting'} lesson (iteration {iteration+1})…")

            try:
                content_raw = call_claude(
                    client,
                    CONTENT_SYSTEM,
                    build_content_prompt(arch, doc, failure_log),
                    max_tokens=4096
                )
                content = safe_json(content_raw)
                if not content:
                    content = {"lesson_title": arch.get("title", "Lesson"),
                               "sections": [], "quizzes": [], "exercises": [],
                               "raw": content_raw}
                ss["content_output"] = content
                ss["agent_states"]["content"] = "done"
            except Exception as e:
                ss["agent_states"]["content"] = "failed"
                prog_bar.progress(100, text=f"❌ Content Agent failed: {e}")
                ss["pipeline_running"] = False
                return

            prog_bar.progress(60, text="🎓 Student Agent: Attempting exercises…")
            time.sleep(0.3)

            # ── STUDENT ───────────────────────────────────────────────────
            ss["agent_states"]["student"] = "running"
            mastery = arch.get("assessment_blueprint", {}).get("mastery_threshold", 0.75)

            try:
                student_raw = call_claude(
                    client,
                    STUDENT_SYSTEM,
                    build_student_prompt(content, persona, mastery),
                    max_tokens=2048
                )
                student = safe_json(student_raw)
                if not student:
                    student = {"persona": persona, "quiz_attempts": [], "exercise_attempts": [],
                               "overall_score": 0.5, "passed": False,
                               "failure_log": "Could not parse student response.",
                               "gaps_identified": [], "raw": student_raw}
                ss["student_output"] = student
                ss["agent_states"]["student"] = "done"
            except Exception as e:
                ss["agent_states"]["student"] = "failed"
                prog_bar.progress(100, text=f"❌ Student Agent failed: {e}")
                ss["pipeline_running"] = False
                return

            score = student.get("overall_score", 0)
            passed = student.get("passed", score >= mastery)
            ss["final_score"] = score

            if passed:
                prog_bar.progress(100, text=f"✅ Student passed with score {score:.0%}! Pipeline complete.")
                ss["agent_states"]["loop"] = "done"
                break
            else:
                failure_log = student.get("failure_log", "") or ""
                gaps = student.get("gaps_identified", [])
                log_entry = {
                    "iteration": iteration + 1,
                    "score": score,
                    "failure_log": failure_log,
                    "gaps": gaps
                }
                ss["rewrite_logs"].append(log_entry)
                ss["agent_states"]["loop"] = "running"
                p = 60 + int(30 * ((iteration+1) / ss["max_iterations"]))
                prog_bar.progress(p, text=f"🔄 Feedback loop {iteration+1}: Rewriting lesson (score was {score:.0%})…")
                time.sleep(0.3)
                if iteration == ss["max_iterations"] - 1:
                    prog_bar.progress(100, text=f"⚠️ Max iterations reached. Final score: {score:.0%}")
                    ss["agent_states"]["loop"] = "failed"

    ss["pipeline_done"] = True
    ss["pipeline_running"] = False

# ─── UI Components ─────────────────────────────────────────────────────────────

def render_agent_status(name: str, role: str, icon: str, icon_class: str, description: str):
    state = st.session_state["agent_states"].get(name.lower(), "idle")
    card_class = {"idle": "", "running": "active", "done": "done", "failed": "failed"}.get(state, "")
    badge_class = {"idle": "badge-idle", "running": "badge-running", "done": "badge-done", "failed": "badge-failed"}.get(state, "badge-idle")
    badge_text = {"idle": "Standby", "running": "Running", "done": "Complete", "failed": "Failed"}.get(state, "idle")

    st.markdown(f"""
    <div class="agent-card {card_class}">
      <div class="agent-header">
        <div class="agent-icon {icon_class}">{icon}</div>
        <div>
          <div class="agent-name">{name}</div>
          <div class="agent-role">{role}</div>
        </div>
        <span class="status-badge {badge_class}">{badge_text}</span>
      </div>
      <div class="agent-desc">{description}</div>
    </div>""", unsafe_allow_html=True)


def render_lesson(content: dict, arch: dict):
    sections = content.get("sections", [])
    quizzes  = content.get("quizzes", [])
    exercises = content.get("exercises", [])

    tabs = st.tabs(["📖 LESSON", "🧪 EXERCISES", "📝 ASSESSMENT", "🗺 OUTLINE"])

    # ── Lesson Tab ────────────────────────────────────────────────────────────
    with tabs[0]:
        if not sections:
            st.info("No sections generated yet.")
        for sec in sections:
            ev_name = sec.get("event_name", "")
            body = sec.get("content", "")
            code = sec.get("code_example")
            visual = sec.get("visual_cue")
            st.markdown(f"""
            <div class="lesson-section">
              <div class="lesson-event-tag">{ev_name}</div>
              <div class="lesson-body">{body}</div>
            """, unsafe_allow_html=True)
            if code:
                st.markdown(f'<div class="code-block">{code}</div>', unsafe_allow_html=True)
            if visual:
                st.markdown(f'<div style="font-size:12px;color:#64748b;margin-top:8px;">💡 <em>{visual}</em></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Exercises Tab ─────────────────────────────────────────────────────────
    with tabs[1]:
        if not exercises:
            st.info("No exercises generated yet.")
        for ex in exercises:
            with st.expander(f"🔬 Exercise {ex.get('id', '?')}: {ex.get('title', 'Exercise')}"):
                st.markdown(f"**Task:** {ex.get('description', '')}")
                if ex.get("starter_code"):
                    st.code(ex["starter_code"], language="python")
                st.markdown(f"**Expected outcome:** {ex.get('expected_output', '')}")
                hints = ex.get("hints", [])
                if hints:
                    with st.expander("💡 Show hints"):
                        for h in hints:
                            st.markdown(f"- {h}")

    # ── Assessment Tab ────────────────────────────────────────────────────────
    with tabs[2]:
        if not quizzes:
            st.info("No quiz generated yet.")
            return
        score_key = "quiz_score_submitted"
        if score_key not in st.session_state:
            st.session_state[score_key] = False

        answers = {}
        with st.form("quiz_form"):
            for q in quizzes:
                st.markdown(f"""
                <div class="quiz-card">
                  <div class="quiz-number">Question {q.get('id', '?')}</div>
                  <div class="quiz-q">{q.get('question', '')}</div>
                </div>""", unsafe_allow_html=True)
                opts = q.get("options", [])
                key = f"quiz_{q.get('id')}"
                answers[key] = st.radio("Select answer:", opts, key=key, label_visibility="collapsed")

            submitted = st.form_submit_button("Submit Assessment")

        if submitted:
            correct = 0
            for q in quizzes:
                key = f"quiz_{q.get('id')}"
                chosen = answers.get(key, "")
                chosen_letter = chosen[0] if chosen else ""
                if chosen_letter == q.get("correct", ""):
                    correct += 1
                    st.success(f"Q{q['id']}: ✅ Correct! {q.get('explanation', '')}")
                else:
                    st.error(f"Q{q['id']}: ❌ Incorrect. Correct answer: {q['correct']}. {q.get('explanation', '')}")
            pct = correct / len(quizzes)
            st.metric("Your Score", f"{pct:.0%}", f"{correct}/{len(quizzes)} correct")

    # ── Outline Tab ───────────────────────────────────────────────────────────
    with tabs[3]:
        if arch:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Learning Objectives**")
                for obj in arch.get("learning_objectives", []):
                    st.markdown(f"- {obj}")
                st.markdown("**Key Concepts**")
                for kc in arch.get("key_concepts", []):
                    st.markdown(f"- {kc}")
            with col2:
                st.markdown("**Prerequisites**")
                for p in arch.get("prerequisite_knowledge", []):
                    st.markdown(f"- {p}")
                st.markdown("**Outline**")
                for s in arch.get("sections", []):
                    st.markdown(f"**{s.get('event_name')}** — {s.get('duration_minutes', '?')} min")
                    st.caption(s.get("content_cues", ""))


def render_student_results(student: dict, arch: dict):
    score  = student.get("overall_score", 0)
    passed = student.get("passed", False)
    persona = student.get("persona", "?")

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-tile">
        <div class="metric-val {'teal' if passed else 'rose'}">{score:.0%}</div>
        <div class="metric-lbl">Overall Score</div>
      </div>
      <div class="metric-tile">
        <div class="metric-val {'teal' if passed else 'rose'}">{'PASS' if passed else 'FAIL'}</div>
        <div class="metric-lbl">Result</div>
      </div>
      <div class="metric-tile">
        <div class="metric-val amber">{persona.title()}</div>
        <div class="metric-lbl">Persona</div>
      </div>
      <div class="metric-tile">
        <div class="metric-val blue">{st.session_state.iteration + 1}</div>
        <div class="metric-lbl">Iterations</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Quiz attempts
    qa = student.get("quiz_attempts", [])
    if qa:
        st.markdown("#### Quiz Attempts")
        for q in qa:
            cls = "result-pass" if q.get("correct") else "result-fail"
            icon = "✅" if q.get("correct") else "❌"
            st.markdown(f"""
            <div class="{cls}">
              <div class="result-label">{icon} Question {q.get('id','?')}</div>
              <div style="font-size:13px;color:#b0bec5;">Chose: {q.get('selected','?')} — {q.get('reasoning','')[:120]}</div>
            </div>""", unsafe_allow_html=True)

    # Exercise attempts
    ea = student.get("exercise_attempts", [])
    if ea:
        st.markdown("#### Exercise Attempts")
        for e in ea:
            cls = "result-pass" if e.get("passed") else "result-fail"
            icon = "✅" if e.get("passed") else "❌"
            with st.expander(f"{icon} Exercise {e.get('id','?')} — Confidence: {e.get('confidence', 0):.0%}"):
                st.code(e.get("attempt_code", ""), language="python")
                if e.get("confusion_points"):
                    st.markdown("**Confusion points:**")
                    for c in e["confusion_points"]:
                        st.markdown(f"- {c}")

    # Failure log
    if not passed and student.get("failure_log"):
        st.markdown("#### Failure Log")
        st.markdown(f'<div class="failure-log">{student["failure_log"]}</div>', unsafe_allow_html=True)

    # Gaps
    gaps = student.get("gaps_identified", [])
    if gaps:
        st.markdown("#### Learning Gaps Identified")
        for g in gaps:
            st.markdown(f"- {g}")


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ Configuration</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">API Access</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Groq API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="gsk_…"
    )
    st.session_state.api_key = api_key

    st.markdown('<div class="sidebar-section">Groq Model</div>', unsafe_allow_html=True)
    groq_model = st.selectbox(
        "Model",
        options=[
            "llama-3.3-70b-versatile",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        index=0,
    )
    st.session_state.groq_model = groq_model
    st.caption("llama-3.3-70b-versatile recommended for best results.")

    st.markdown('<div class="sidebar-section">Pedagogy Framework</div>', unsafe_allow_html=True)
    framework = st.selectbox(
        "Instructional Design Model",
        options=["gagne", "merrill"],
        format_func=lambda x: "Gagné's 9 Events" if x == "gagne" else "Merrill's First Principles",
        index=0 if st.session_state.framework == "gagne" else 1
    )
    st.session_state.framework = framework

    if framework == "gagne":
        st.caption("Maps content to 9 events: Attention → Objectives → Recall → Content → Guidance → Performance → Feedback → Assessment → Retention")
    else:
        st.caption("Problem-centred task at the core, with Activation → Demonstration → Application → Integration phases")

    st.markdown('<div class="sidebar-section">Student Simulator</div>', unsafe_allow_html=True)
    persona = st.selectbox(
        "Student Persona",
        options=["novice", "intermediate", "advanced"],
        index=["novice", "intermediate", "advanced"].index(st.session_state.student_persona)
    )
    st.session_state.student_persona = persona

    max_iter = st.slider("Max Feedback Iterations", 1, 5, st.session_state.max_iterations)
    st.session_state.max_iterations = max_iter

    st.markdown('<div class="sidebar-section">Pipeline Status</div>', unsafe_allow_html=True)
    for agent, label in [("architect", "🔭 Architect"), ("content", "✍️ Content"),
                          ("student", "🎓 Student"), ("loop", "🔄 Feedback Loop")]:
        state = st.session_state["agent_states"][agent]
        icon = {"idle": "⚪", "running": "🟡", "done": "🟢", "failed": "🔴"}.get(state, "⚪")
        st.markdown(f"{icon} {label}: **{state.title()}**")

    if st.session_state.pipeline_done:
        score = st.session_state.final_score
        if score is not None:
            st.markdown("---")
            st.metric("Final Mastery Score", f"{score:.0%}")

    st.markdown("---")
    if st.button("🔄 Reset Pipeline"):
        keys_to_clear = ["architect_output", "content_output", "student_output",
                          "pipeline_done", "pipeline_running", "rewrite_logs",
                          "final_score", "iteration"]
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state["agent_states"] = {"architect": "idle", "content": "idle", "student": "idle", "loop": "idle"}
        st.rerun()

# ─── Main Layout ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-label">// Multi-Agent System v1.0</div>
  <h1>PedagogyOS<br><span>Autonomous Curriculum Engine</span></h1>
  <div class="hero-sub">
    Feed raw technical documentation. Three AI agents — Architect, Content Writer, and Simulated Student — 
    collaborate in a self-correcting loop to produce verified, pedagogically-sound lesson plans.<br>
    <span style="font-size:12px;color:#4ade80;">⚡ Powered by Groq's ultra-fast inference</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Two-column layout: Input + Agent Monitor ──────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown("### 📄 Raw Documentation Input")
    raw_doc = st.text_area(
        "Paste technical documentation, API reference, SDK guide or any raw text",
        value=st.session_state.raw_doc,
        height=280,
        placeholder="Paste your raw SDK documentation, API reference, or any technical content here…\n\nExample: A library README, a function reference, a configuration guide, etc."
    )
    st.session_state.raw_doc = raw_doc

    # Quick load example
    col_ex, col_run = st.columns([1, 2])
    with col_ex:
        if st.button("📋 Load SDK Example"):
            st.session_state.raw_doc = """Anthropic Python SDK — Quick Reference

The anthropic package is the official Python SDK.

Installation: pip install anthropic

Basic Usage:
  from groq import Groq
  client = Groq(api_key="YOUR_GROQ_API_KEY")
  chat_completion = client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      messages=[{"role": "user", "content": "Hello!"}],
      max_tokens=1024,
  )
  print(chat_completion.choices[0].message.content)

Models: llama-3.3-70b-versatile, llama3-70b-8192, llama3-8b-8192, mixtral-8x7b-32768, gemma2-9b-it
Context Window: up to 128k tokens (model-dependent)

Streaming:
  stream = client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      messages=[{"role": "user", "content": "Hello!"}],
      stream=True,
  )
  for chunk in stream:
      print(chunk.choices[0].delta.content or "", end="")

System Prompts:
  messages=[{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}]

Tool Use (Function Calling):
  Pass tools as a list of dicts with name, description, and parameters (JSON Schema).
  The model returns tool_calls; you execute and return results as "tool" role messages.

Error Handling: Catch groq.APIConnectionError, RateLimitError, AuthenticationError.
Rate Limits: Free tier has per-minute and per-day token limits per model.
"""
            st.rerun()

    with col_run:
        run_clicked = st.button("🚀 Run Curriculum Engine", use_container_width=True)

with right:
    st.markdown("### 🤖 Agent Monitor")
    render_agent_status(
        "Architect Agent", "THE PEDAGOGUE", "🔭", "icon-architect",
        "Maps raw documentation to the chosen instructional framework (Gagné/Merrill), generating a structured blueprint."
    )
    st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)
    render_agent_status(
        "Content Agent", "THE DEVELOPER", "✍️", "icon-content",
        "Generates the full lesson text, code examples, exercises and assessments from the Architect's blueprint."
    )
    st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)
    render_agent_status(
        "Student Agent", "THE VALIDATOR", "🎓", "icon-student",
        f"Simulates a {st.session_state.student_persona} student attempting all exercises. Generates failure logs if mastery is not met."
    )
    st.markdown('<div class="pipeline-arrow">↓</div>', unsafe_allow_html=True)
    render_agent_status(
        "Feedback Loop", "DYNAMIC REWRITE", "🔄", "icon-loop",
        "On failure, the Architect reviews gaps and the Content Agent rewrites confusing sections. Loops until mastery is achieved."
    )

# ─── Run Pipeline ──────────────────────────────────────────────────────────────
if run_clicked:
    if not st.session_state.api_key.strip():
        st.error("⚠️ Please enter your Groq API key in the sidebar. Get one free at console.groq.com")
    elif not st.session_state.raw_doc.strip():
        st.error("⚠️ Please paste some documentation to generate a curriculum from.")
    else:
        client = get_client()
        prog_placeholder = st.empty()
        with prog_placeholder.container():
            run_pipeline(
                client,
                st.session_state.raw_doc,
                st.session_state.framework,
                st.session_state.student_persona,
                prog_placeholder
            )
        st.rerun()

# ─── Results Section ───────────────────────────────────────────────────────────
if st.session_state.pipeline_done and st.session_state.content_output:
    st.markdown("---")
    st.markdown("## 🎓 Generated Curriculum")

    arch    = st.session_state.architect_output or {}
    content = st.session_state.content_output or {}
    student = st.session_state.student_output  or {}

    # Summary metrics
    score = st.session_state.final_score or 0
    passed = student.get("passed", False)
    iters  = st.session_state.iteration + 1

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-tile">
        <div class="metric-val teal">{arch.get('difficulty', '—').title()}</div>
        <div class="metric-lbl">Difficulty</div>
      </div>
      <div class="metric-tile">
        <div class="metric-val blue">{arch.get('estimated_minutes', '—')} min</div>
        <div class="metric-lbl">Est. Duration</div>
      </div>
      <div class="metric-tile">
        <div class="metric-val amber">{len(content.get('sections', []))}</div>
        <div class="metric-lbl">Sections</div>
      </div>
      <div class="metric-tile">
        <div class="metric-val {'teal' if passed else 'rose'}">{score:.0%}</div>
        <div class="metric-lbl">Student Score</div>
      </div>
      <div class="metric-tile">
        <div class="metric-val">{iters}</div>
        <div class="metric-lbl">Iterations</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Lesson title
    title = content.get("lesson_title") or arch.get("title", "Generated Lesson")
    fw_label = "Gagné's 9 Events" if arch.get("framework", "gagne") == "gagne" else "Merrill's First Principles"
    st.markdown(f"### {title}")
    st.caption(f"Framework: {fw_label} · {arch.get('topic_summary', '')}")

    # Main lesson tabs
    result_tabs = st.tabs(["📚 LESSON CONTENT", "🎓 STUDENT RESULTS", "🔄 REWRITE LOGS", "🗂 RAW JSON"])

    with result_tabs[0]:
        render_lesson(content, arch)

    with result_tabs[1]:
        if student:
            render_student_results(student, arch)
        else:
            st.info("Student simulation results will appear here after the pipeline runs.")

    with result_tabs[2]:
        logs = st.session_state.rewrite_logs
        if not logs:
            if passed:
                st.success("✅ Student passed on first attempt — no rewrites needed!")
            else:
                st.info("Rewrite logs will appear here if the student fails and the lesson is revised.")
        else:
            for log in logs:
                with st.expander(f"Iteration {log['iteration']} — Score: {log['score']:.0%}", expanded=True):
                    st.markdown(f"**Student Score:** {log['score']:.0%}")
                    st.markdown("**Failure Log:**")
                    st.markdown(f'<div class="failure-log">{log["failure_log"]}</div>', unsafe_allow_html=True)
                    if log.get("gaps"):
                        st.markdown("**Learning Gaps:**")
                        for g in log["gaps"]:
                            st.markdown(f"- {g}")

    with result_tabs[3]:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Architect Output**")
            st.json(arch, expanded=False)
        with col_b:
            st.markdown("**Student Output**")
            st.json(student, expanded=False)
        st.markdown("**Content Output**")
        st.json(content, expanded=False)

elif not st.session_state.pipeline_done:
    # Instructions panel
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(13,18,25,0.8); border: 1px solid #1e2d3d; border-radius: 12px; padding: 32px 40px; text-align: center; margin-top: 20px;">
      <div style="font-size: 48px; margin-bottom: 16px;">🧬</div>
      <div style="font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 12px;">
        Ready to transform your documentation
      </div>
      <div style="font-size: 14px; color: #64748b; line-height: 1.8; max-width: 520px; margin: 0 auto;">
        1. Enter your Anthropic API key in the sidebar<br>
        2. Paste raw technical documentation in the input box<br>
        3. Choose your pedagogical framework and student persona<br>
        4. Hit <strong style="color: #00d4aa">Run Curriculum Engine</strong> and watch the agents collaborate
      </div>
    </div>
    """, unsafe_allow_html=True)
