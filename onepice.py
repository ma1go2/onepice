import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import json

df = pd.read_excel("onepice_count_v1.1.xlsx")

st.title("🧩 원피스 캐릭터 조합 도우미")

tiers = sorted(df['등급'].dropna().unique())
selected_tier = st.selectbox("등급 선택", tiers)
filtered_names = df[df['등급'] == selected_tier]['캐릭터 이름'].dropna().unique()
selected_name = st.selectbox("캐릭터 선택", filtered_names)

exclude_names = st.multiselect("제외할 하위 캐릭터 선택", df['캐릭터 이름'].unique())

tier_y_positions = {
    "영원한": -550, "불멸의": -500,
    "초월함": -400, "신비함": -300, "제한됨": -200,
    "전설적인": -100, "히든조합": -50,
    "변화됨":-70,
    "희귀함": 0, "랜덤전용": 100,
    "특별함": 200, "안흔함": 300, "흔함": 400
}

tier_colors = {
    "영원한": "#8B0000",       # DarkRed
    "불멸의": "#B22222",       # FireBrick
    "초월함": "#FF4500",       # OrangeRed
    "신비함": "#FF8C00",       # DarkOrange
    "제한됨": "#DAA520",       # GoldenRod
    "전설적인": "#228B22",     # ForestGreen
    "히든조합": "#2E8B57",     # SeaGreen
    "희귀함": "#1E90FF",       # DodgerBlue
    "랜덤전용": "#4169E1",     # RoyalBlue
    "특별함": "#6A5ACD",       # SlateBlue
    "안흔함": "#9370DB",       # MediumPurple
    "흔함": "#708090"          # SlateGray
}

net = Network(height="1000px", width="100%", directed=True)

final_materials = set()
node_ids = set()

def add_node(name, tier, parent=None, x_offset=0, depth=0):
    if name in exclude_names:
        return

    label = f"{name} ({tier})"
    node_id = f"{name}__{tier}"
    if node_id in node_ids:
        if parent:
            net.add_edge(parent, label)
        return
    node_ids.add(node_id)

    try:
        img_url = df[(df['캐릭터 이름'] == name) & (df['등급'] == tier)]['이미지'].values[0]
    except:
        img_url = ""

    title = f"{label}"
    if img_url:
        # 이미지 크기 확대 (width=100)
        title += f"<br><img src='{img_url}' width='100'>"

    color = tier_colors.get(tier, "#dddddd")
    y_pos = tier_y_positions.get(tier, 0)

    net.add_node(
        label,
        label=label,
        title=title,
        shape='circularImage' if img_url else 'ellipse',
        image=img_url,
        color=color,
        x=x_offset,
        y=y_pos,
        fixed={"x": False, "y": True},
        physics=False
    )

    if parent:
        net.add_edge(parent, label)

    try:
        row = df[(df['캐릭터 이름'] == name) & (df['등급'] == tier)]
        r = row['조합정보'].values[0]
        sub_combos = eval(r) if isinstance(r, str) else []
        has_combo = False

        base_spread = 300
        spread = base_spread * (1 + 0.3 * depth)

        for i, item in enumerate(sub_combos):
            if "(" in item:
                sub_name, sub_tier = item.rsplit("(", 1)
                sub_name = sub_name.strip()
                sub_tier = sub_tier.replace(")", "").strip()
                offset = x_offset + (i - (len(sub_combos) - 1) / 2) * spread
                add_node(sub_name, sub_tier, parent=label, x_offset=offset, depth=depth + 1)
                has_combo = True
        if not has_combo:
            final_materials.add(label)
    except:
        final_materials.add(label)

if st.button("🔍 조합 트리 보기"):
    if selected_name:
        final_materials.clear()
        node_ids.clear()
        add_node(selected_name, selected_tier)

        net.set_options(json.dumps({
            "nodes": {
                "borderWidth": 2,
                "size": 25,
                "font": {"size": 16},
                "shadow": True
            },
            "edges": {
                "arrows": "to",
                "smooth": True,
                "shadow": True,
                "color": {
                    "inherit": False,
                    "color": "#cccccc",
                    "highlight": "#ff0000"
                }
            },
            "layout": {
                "hierarchical": {
                    "enabled": False
                }
            },
            "physics": {
                "enabled": True
            },
            "interaction": {
                "hover": True,
                "navigationButtons": True,
                "multiselect": True,
                "dragNodes": True
            }
        }))

        net.save_graph("tree.html")
        components.html(open("tree.html", "r", encoding="utf-8").read(), height=1000, scrolling=True)

if st.button("📦 최종 재료 보기"):
    if final_materials:
        st.subheader("🧱 최종 재료 목록 (더 이상 분해되지 않는 캐릭터)")
        for mat in sorted(final_materials):
            st.markdown(f"✅ {mat}")
    else:
        st.info("먼저 조합 트리를 생성해주세요.")
