# app.py — Improved Social Media Agent (Groq)
import os
import json
import textwrap
import streamlit as st
import pandas as pd
from groq import Groq
from typing import Optional, Dict, Any, List

# ---------- Configuration ----------
DEFAULT_MODEL = "llama-3.3-70b-versatile"   # higher-quality, current 70B replacement
FAST_MODEL = "llama-3.1-8b-instant"          # faster, lower cost (also free)
DEFAULT_MAX_TOKENS = 800

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Social Media Agent (Groq)", layout="centered")
st.title("🧠 Social Media Agent ")

st.markdown(
    "Enter a topic, pick platform/tone, then click **Generate**. "
    "The model will return captions, hashtags, and a 7-day plan."
)

# ---------- UI: Inputs ----------
with st.form("prompt_form"):
    topic = st.text_input("Topic / Product / Theme", value="Eco-friendly water bottle")
    platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Twitter (X)", "Facebook"])
    tone = st.selectbox("Tone / Voice", ["Casual", "Professional", "Funny", "Inspirational"])
    num_captions = st.slider("Number of captions", 1, 6, 3)
    model_choice = st.selectbox("Model (choose quality vs speed)", [DEFAULT_MODEL, FAST_MODEL])
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.7, 0.05)
    submit = st.form_submit_button("Generate")

# ---------- Helper: prompt builder (request JSON) ----------
def build_prompt(topic: str, platform: str, tone: str, num_captions: int) -> str:
    prompt = f"""
You are a social media copywriter. Produce output for the following request.

Task:
- Create {num_captions} distinct captions for {platform} about: "{topic}"
- Each caption must be short (1-2 lines). Include a CTA in at least one caption.
- Provide 6 relevant hashtags (as a list).
- Provide a 7-day content plan: list one short idea per day.

REQUIREMENTS:
- Tone: {tone}
- Output MUST be valid JSON in the following structure (no extra commentary):

{{
  "captions": [
    {{"text": "Caption 1 text"}},
    {{"text": "Caption 2 text"}}
  ],
  "hashtags": ["tag1", "tag2", "..."],
  "plan": [
    {{"day": "Day 1", "idea": "Short idea"}},
    {{"day": "Day 2", "idea": "Short idea"}}
  ]
}}

Return ONLY the JSON object. If you cannot produce full JSON, clearly label sections CAPTIONS, HASHTAGS, PLAN in plain text.
"""
    return textwrap.dedent(prompt)

# ---------- Helper: call Groq ----------
def call_groq(prompt: str, model: str, max_tokens: int = DEFAULT_MAX_TOKENS, temperature: float = 0.7) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    # Groq response structure: response.choices[0].message.content
    raw = resp.choices[0].message.content
    return {"raw": raw, "resp_obj": resp}

# ---------- Helper: parse output ----------
def parse_json_or_sections(raw: str) -> Dict[str, Any]:
    # Try JSON parse first
    raw_stripped = raw.strip()
    try:
        # If the model returned JSON but with code fences, remove them
        if raw_stripped.startswith("```"):
            # remove leading and trailing ``` blocks
            parts = raw_stripped.split("```")
            # choose the middle block if available
            if len(parts) >= 3:
                raw_stripped = parts[1].strip()
            else:
                raw_stripped = raw_stripped.strip("` \n")
        data = json.loads(raw_stripped)
        return {"parsed": data, "method": "json"}
    except Exception:
        # Fallback: simple section parsing
        sections = {"captions": [], "hashtags": [], "plan": []}
        lines = raw.splitlines()
        cur = None
        for ln in lines:
            l = ln.strip()
            if not l:
                continue
            up = l.upper()
            if up.startswith("CAPTIONS"):
                cur = "captions"; continue
            if up.startswith("HASHTAGS"):
                cur = "hashtags"; continue
            if up.startswith("PLAN"):
                cur = "plan"; continue
            if cur == "captions":
                # remove numbering like "1." or "- "
                txt = l.lstrip("0123456789. -—")
                sections["captions"].append({"text": txt})
            elif cur == "hashtags":
                # split by commas
                tags = [t.strip().lstrip("#") for t in l.split(",") if t.strip()]
                sections["hashtags"].extend(tags)
            elif cur == "plan":
                # lines like "Day 1: idea"
                if ":" in l:
                    day, idea = l.split(":", 1)
                    sections["plan"].append({"day": day.strip(), "idea": idea.strip()})
                else:
                    sections["plan"].append({"day": "", "idea": l})
            else:
                # nothing matched yet; ignore
                pass
        return {"parsed": sections, "method": "sections"}

# ---------- Helper: copy button using JS ----------
def copy_button(text: str, key: str):
    # small HTML + JS to copy text to clipboard
    html = f"""
    <button id="btn_{key}">Copy</button>
    <script>
    const btn = document.getElementById("btn_{key}");
    btn.onclick = () => navigator.clipboard.writeText({json.dumps(text)});
    </script>
    """
    st.components.v1.html(html, height=35)

# ---------- Maintain history ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Generate if submitted ----------
if submit:
    if not topic.strip():
        st.error("Please provide a topic.")
    else:
        prompt = build_prompt(topic, platform, tone, num_captions)
        st.info("Calling the model... this may take a few seconds.")
        try:
            result = call_groq(prompt, model_choice, max_tokens=DEFAULT_MAX_TOKENS, temperature=temperature)
            raw = result["raw"]
            parse = parse_json_or_sections(raw)
            parsed = parse["parsed"]

            # Normalize parsed to contain lists/safe structures
            captions = parsed.get("captions", []) if isinstance(parsed, dict) else []
            hashtags = parsed.get("hashtags", []) if isinstance(parsed, dict) else []
            plan = parsed.get("plan", []) if isinstance(parsed, dict) else []

            # If captions are strings, convert
            normalized_captions = []
            for c in captions:
                if isinstance(c, str):
                    normalized_captions.append({"text": c})
                elif isinstance(c, dict) and "text" in c:
                    normalized_captions.append({"text": c["text"]})
                else:
                    # try to stringify
                    normalized_captions.append({"text": str(c)})

            # store in history
            entry = {
                "topic": topic,
                "platform": platform,
                "tone": tone,
                "captions": normalized_captions,
                "hashtags": hashtags,
                "plan": plan,
                "raw": raw,
            }
            st.session_state.history.insert(0, entry)

            # ---------- Display nicely ----------
            st.success("Content generated ✅")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Captions")
                for i, c in enumerate(normalized_captions, start=1):
                    st.markdown(f"**{i}.** {c['text']}")
                    # copy button per caption
                    copy_button(c["text"], key=f"cap_{len(st.session_state.history)}_{i}")

            with col2:
                st.subheader("Hashtags")
                if hashtags:
                    tags_line = " ".join([("#" + t if not t.startswith("#") else t) for t in hashtags])
                    st.write(tags_line)
                    copy_button(tags_line, key=f"tags_{len(st.session_state.history)}")
                else:
                    st.write("—")

            st.markdown("---")
            st.subheader("7-day Content Plan")
            if plan:
                for p in plan:
                    day = p.get("day", "")
                    idea = p.get("idea", "") if isinstance(p.get("idea", ""), str) else json.dumps(p.get("idea", ""))
                    st.markdown(f"**{day}** — {idea}")
            else:
                st.write("—")

            # raw output expandable
            with st.expander("Raw model output"):
                st.code(raw)

            # ---------- Export: CSV (captions) and TXT ----------
            # CSV for captions
            df_caps = pd.DataFrame([{"caption": c["text"]} for c in normalized_captions])
            csv = df_caps.to_csv(index=False)
            st.download_button("Download captions as CSV", data=csv, file_name="captions.csv", mime="text/csv")

            # TXT full raw
            st.download_button("Download raw output (TXT)", data=raw, file_name="social_media_output.txt")

        except Exception as e:
            st.error(f"Error from Groq API: {e}")
            st.exception(e)

# ---------- Show generation history ----------
if st.session_state.history:
    st.markdown("---")
    st.subheader("Recent generations")
    for idx, h in enumerate(st.session_state.history[:5]):
        with st.expander(f"{h['topic']} — {h['platform']} ({h['tone']})"):
            for i, c in enumerate(h["captions"], start=1):
                st.write(f"**{i}.** {c['text']}")
            if h["hashtags"]:
                st.write("Hashtags:", " ".join(["#"+t.lstrip("#") for t in h["hashtags"]]))
            if h["plan"]:
                st.write("Plan:")
                for p in h["plan"]:
                    day = p.get("day", "")
                    idea = p.get("idea", "")
                    st.write(f"- {day}: {idea}")
            st.download_button(f"Download raw output #{idx+1}", data=h["raw"], file_name=f"raw_output_{idx+1}.txt")

# ---------- Footer ----------
st.markdown("---")
st.caption("Built with Groq (free models).")
