import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Page setup
st.set_page_config(page_title="Concept Map Builder", layout="wide")
st.markdown("<h1 style='text-align:center; color: #4B8BBE;'>🧠 Concept Map Builder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px; color: #306998;'>Create and connect your own ideas. Reflect. Learn deeply.</p>", unsafe_allow_html=True)
st.markdown("---")

# Session state setup
if "concepts" not in st.session_state:
    st.session_state.concepts = []
if "connections" not in st.session_state:
    st.session_state.connections = []
if "explanations" not in st.session_state:
    st.session_state.explanations = {}

# Layout: two columns for input forms
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📌 Concepts")
    with st.form("add_concept", clear_on_submit=True):
        new_concept = st.text_input("Add a concept (node):", help="Type a new idea or term you want to learn about")
        submitted = st.form_submit_button("➕ Add Concept")
        if submitted:
            if not new_concept.strip():
                st.warning("Please enter a non-empty concept.")
            elif new_concept in st.session_state.concepts:
                st.warning("Concept already exists.")
            else:
                st.session_state.concepts.append(new_concept)
                st.success(f"Concept '{new_concept}' added!")

    st.markdown("**Current Concepts:**")
    if st.session_state.concepts:
        st.write(", ".join(st.session_state.concepts))
    else:
        st.write("_No concepts added yet._")

with col2:
    st.subheader("🔗 Create Connection")
    if len(st.session_state.concepts) < 2:
        st.info("Add at least two concepts to create connections.")
    else:
        with st.form("add_connection", clear_on_submit=True):
            source = st.selectbox("From:", st.session_state.concepts, key="source")
            target = st.selectbox("To:", st.session_state.concepts, key="target")
            label = st.text_input("Label this connection (e.g. 'causes', 'part of'):", help="Describe the relationship")
            explanation = st.text_area("Why are these concepts connected?", help="Write a short explanation for your connection")
            submitted = st.form_submit_button("🔗 Create Connection")
            if submitted:
                if source == target:
                    st.error("Cannot connect a concept to itself.")
                elif not label.strip():
                    st.error("Please add a label for the connection.")
                else:
                    st.session_state.connections.append((source, target, label))
                    st.session_state.explanations[(source, target)] = explanation
                    st.success(f"Connection '{source} → {target}' added!")

st.markdown("---")

# Display connections
if st.session_state.connections:
    st.subheader("🧩 Concept Connections")
    for src, tgt, lbl in st.session_state.connections:
        exp = st.session_state.explanations.get((src, tgt), "")
        st.markdown(f"**{src} → {tgt}** *(label: {lbl})*\n> _{exp}_")

# Visual map
if st.session_state.connections:
    st.subheader("🗺️ Visual Map")
    G = nx.DiGraph()
    for concept in st.session_state.concepts:
        G.add_node(concept)
    for src, tgt, lbl in st.session_state.connections:
        G.add_edge(src, tgt, label=lbl)

    pos = nx.spring_layout(G, seed=42)  # fixed seed for consistent layout
    fig, ax = plt.subplots(figsize=(10, 6))  # wider figure to fit nodes
    nx.draw_networkx_nodes(G, pos, node_color='#82c91e', node_size=1800, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', ax=ax)
    nx.draw_networkx_edges(G, pos, arrowsize=25, arrowstyle='-|>', ax=ax)

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='#333333', font_size=10, ax=ax)

    plt.tight_layout()
    ax.set_axis_off()  # hide axes for clean look
    st.pyplot(fig)

st.markdown("---")

# Export and Clear
col3, col4 = st.columns(2)

with col3:
    if st.button("📋 Copy Concept Map to Clipboard"):
        text_out = "Concept Map:\n"
        for src, tgt, lbl in st.session_state.connections:
            exp = st.session_state.explanations.get((src, tgt), "")
            text_out += f"{src} -> {tgt} (label: {lbl})\nReason: {exp}\n\n"
        st.code(text_out, language="text")

with col4:
    if st.button("🗑️ Clear Map"):
        st.session_state.concepts = []
        st.session_state.connections = []
        st.session_state.explanations = {}
        st.success("Map cleared! Please refresh the page to start fresh.")

if st.button("💾 Download as .txt"):
    buffer = BytesIO()
    text_out = "Concept Map:\n"
    for src, tgt, lbl in st.session_state.connections:
        exp = st.session_state.explanations.get((src, tgt), "")
        text_out += f"{src} -> {tgt} (label: {lbl})\nReason: {exp}\n\n"
    buffer.write(text_out.encode())
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="concept_map.txt">⬇️ Download Concept Map</a>'
    st.markdown(href, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#777;'>Built with ❤️ to help you think deeply and learn effectively.</p>", unsafe_allow_html=True)
