import streamlit as st
from groq import Groq

# ----------------------------
# 1) Osnovne nastavitve strani
# ----------------------------
st.set_page_config(
    page_title="Pametni klepetalnik",
    page_icon="💬",
    layout="centered"
)

# ----------------------------
# 2) Stil (osnovna uskladitev)
#    (lahko prilagodiš barve)
# ----------------------------
st.markdown("""
<style>
/* ozadje */
.stApp {
    background-color: #0f172a; /* temno modra */
}

/* naslov */
h1, h2, h3, p, li, label {
    color: #e2e8f0 !important;
}

/* input */
[data-testid="stChatInput"] textarea {
    background-color: #111827 !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
}

/* chat mehurčki */
[data-testid="stChatMessage"] {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

st.title("💬 Pametni klepetalnik")

# ----------------------------
# 3) Specializacija (OBVEZNO)
# ----------------------------
PODROCJE = "Ljubljana"  # <-- TU zamenjaj s temo svoje strani
MEJE = (
    "Odgovarjaj samo na vprašanja, ki so neposredno povezana s področjem: "
    f"'{PODROCJE}'. Če uporabnik vpraša karkoli izven tega področja, "
    "vljudno povej, da za to nimaš informacij, in ga usmeri nazaj na področje. "
    "Ne ugibaj in ne odgovarjaj na splošne teme. "
    "Komunikacija mora potekati izključno v slovenščini. "
    "Odgovori naj bodo pregledni, slovnično pravilni in lepo oblikovani."
)

SYSTEM = f"Si prijazen asistent, strokovnjak za področje: {PODROCJE}. {MEJE}"

# ----------------------------
# 4) Groq klient (API ključ iz Secrets)
# ----------------------------
# Streamlit Cloud: st.secrets["GROQ_API_KEY"]
# Lokalno: lahko dodaš .streamlit/secrets.toml, ampak tega NE pushaj javno
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Manjka GROQ_API_KEY. Dodaj ga v Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

MODEL = "llama-3.3-70b-versatile"
MAX_MESSAGES = 10  # omejitev zgodovine (da ne kuriš tokenov)

# ----------------------------
# 5) Spomin v seji (session_state)
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM}
    ]

# Gumb za ročni reset (koristno za testiranje)
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🔄 Reset"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM}]
        st.rerun()

with col2:
    st.caption(f"Specializacija: **{PODROCJE}**")

# ----------------------------
# 6) Prikaz zgodovine (brez system sporočila)
# ----------------------------
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# ----------------------------
# 7) Vnos uporabnika (namesto input())
# ----------------------------
user_text = st.chat_input("Vpiši vprašanje ...")

if user_text:
    # prikaz uporabnika
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # obrez zgodovine (pusti system + zadnjih N-1)
    if len(st.session_state.messages) > MAX_MESSAGES:
        # indeks 0 je system, zato režemo od 1 naprej
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-(MAX_MESSAGES-1):]

    # klic modela
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=st.session_state.messages,
            temperature=0.4
        )
        ai_text = response.choices[0].message.content

    except Exception as e:
        ai_text = f"Prišlo je do napake pri povezavi z modelom: `{e}`"

    # prikaz asistenta
    st.session_state.messages.append({"role": "assistant", "content": ai_text})
    with st.chat_message("assistant"):
        st.markdown(ai_text)

    # token usage (opcijsko, za debug)
    try:
        usage = response.usage
        with st.expander("📊 Poraba žetonov"):
            st.write(f"- Vprašanje (prompt): {usage.prompt_tokens}")
            st.write(f"- Odgovor (completion): {usage.completion_tokens}")
            st.write(f"- Skupaj: {usage.total_tokens}")
    except Exception:
        pass