import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from io import BytesIO
from reportlab.lib.pagesizes import A4

from career_data import CAREER_SKILLS
from skill_graph import build_skill_graph, recommend_learning_path
from job_matcher import recommend_jobs

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def create_pdf_report(result):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    content = []

    content.append(
        Paragraph("SkillGraph AI - Skill Gap Report", styles["Title"])
    )
    content.append(Spacer(1, 20))

    content.append(Paragraph("Student Profile", styles["Heading2"]))

    profile_data = [
        ["Student Name", result["name"]],
        ["Education", result["education"]],
        ["Target Career", result["career"]],
        ["Career Match", f'{result["percentage"]}%'],
    ]

    profile_table = Table(profile_data, colWidths=[130, 330])
    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    content.append(profile_table)
    content.append(Spacer(1, 20))

    content.append(Paragraph("Skills You Have", styles["Heading2"]))

    matched = result["matched"] or ["No matching skills yet"]
    for skill in matched:
        content.append(Paragraph(f"- {skill}", styles["BodyText"]))

    content.append(Spacer(1, 15))
    content.append(Paragraph("Skills to Learn", styles["Heading2"]))

    missing = result["missing"] or ["No missing skills"]
    for skill in missing:
        content.append(Paragraph(f"- {skill}", styles["BodyText"]))

    content.append(Spacer(1, 20))
    content.append(Paragraph(
        "Note: This prototype compares your selected skills "
        "against sample career requirements. It is not a "
        "validated job-readiness score.",
        styles["Italic"]
    ))

    doc.build(content)
    buffer.seek(0)

    return buffer.getvalue()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SkillGraph AI",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 SkillGraph AI")
st.subheader("Personalized Skill Gap Analysis & Career Recommendation")
st.write(
    "Discover your skills, identify career skill gaps, "
    "and explore a learning path through an interactive skill graph."
)

st.divider()


# ---------------- STUDENT PROFILE ----------------
st.header("👩‍🎓 Student Profile")

name = st.text_input("Enter your name")

education = st.selectbox(
    "Select your education",
    ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate"]
)

career = st.selectbox(
    "Choose your target career",
    list(CAREER_SKILLS.keys())
)


# ---------------- SKILLS ----------------
st.header("💻 Your Current Skills")

all_skills = sorted({
    skill
    for skill_list in CAREER_SKILLS.values()
    for skill in skill_list
})

current_skills = st.multiselect(
    "Select the skills you already know",
    all_skills,
    default=[
        skill for skill in ["Python", "SQL"]
        if skill in all_skills
    ]
)


# ---------------- ANALYSIS ----------------
if st.button("Analyze My Skills 🚀", type="primary"):

    if not name.strip():
        st.warning("Please enter your name.")
        st.stop()

    if not current_skills:
        st.warning("Please select at least one skill.")
        st.stop()

    current = set(current_skills)
    required = set(CAREER_SKILLS[career])

    matched = sorted(current & required)
    missing = sorted(required - current)

    percentage = round(len(matched) / len(required) * 100)

    st.session_state["analysis"] = {
        "name": name.strip(),
        "education": education,
        "career": career,
        "current": current,
        "required": required,
        "matched": matched,
        "missing": missing,
        "percentage": percentage
    }


# ---------------- DISPLAY RESULTS ----------------
if "analysis" in st.session_state:

    result = st.session_state["analysis"]

    # Recalculate if the user changes career or skills.
    # A new click on Analyze My Skills saves the updated selection.
    if result["career"] != career:
        st.info("Click Analyze My Skills to update the report for your new career.")

    st.divider()
    st.header("📊 Your Skill Gap Report")

    st.write(f"**Student:** {result['name']}")
    st.write(f"**Education:** {result['education']}")
    st.write(f"**Target Career:** {result['career']}")

   # Download PDF report
    pdf_data = create_pdf_report(result)

    st.download_button(
        label="📄 Download My Skill Report (PDF)",
        data=pdf_data,
        file_name="SkillGraph_AI_Report.pdf",
        mime="application/pdf"
    )

    # ---------------- DOWNLOAD CSV REPORT ----------------
    report_data = {
        "Category": (
            ["Student"] * 1
            + ["Education"] * 1
            + ["Target Career"] * 1
            + ["Career Match"] * 1
            + ["Matched Skill"] * len(result["matched"])
            + ["Skill to Learn"] * len(result["missing"])
        ),
        "Details": (
            [result["name"]]
            + [result["education"]]
            + [result["career"]]
            + [f"{result['percentage']}%"]
            + result["matched"]
            + result["missing"]
        )
    }

    report_df = pd.DataFrame(report_data)

    st.download_button(
        label="📥 Download My Skill Report (CSV)",
        data=report_df.to_csv(index=False).encode("utf-8"),
        file_name="SkillGraph_AI_Report.csv",
        mime="text/csv"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Required Skills", len(result["required"]))
    col2.metric("Skills Matched", len(result["matched"]))
    col3.metric("Skills to Learn", len(result["missing"]))

    st.subheader("🎯 Career Skill Match")
    st.metric("Required skills matched", f"{result['percentage']}%")
    st.progress(result["percentage"] / 100)

    if result["percentage"] < 40:
        st.info("🌱 Good start! Focus on building your foundation skills.")
    elif result["percentage"] < 70:
        st.info("🚀 You're making progress! Keep learning the missing skills.")
    else:
        st.success("🎉 Great progress! Review the remaining skills to strengthen your profile.")
    left, right = st.columns(2)

    with left:
        st.subheader("✅ Skills You Have")
        if result["matched"]:
            for skill in result["matched"]:
                st.write(f"✓ {skill}")
        else:
            st.info("No matching skills yet.")

    with right:
        st.subheader("📚 Skills to Learn")
        if result["missing"]:
            for skill in result["missing"]:
                st.write(f"• {skill}")
        else:
            st.success("You have all the skills in this career's sample list!")

    # ---------------- ALTERNATIVE JOB RECOMMENDATIONS ----------------
    st.divider()
    st.header("💼 Jobs Matching Your Current Skills")

    job_matches = recommend_jobs(result["current"])

    if job_matches:
        st.write(
            "These job roles are ranked by how closely your "
            "current skills match their sample requirements."
        )

        for job in job_matches:
            with st.expander(
                f'{job["job_title"]} — {job["percentage"]}% skill match'
            ):
                st.progress(job["percentage"] / 100)

                st.write("✅ **Matched skills**")
                if job["matched"]:
                    st.write(", ".join(job["matched"]))
                else:
                    st.write("No matching skills yet.")

                st.write("📚 **Skills to learn**")
                if job["missing"]:
                    st.write(", ".join(job["missing"]))
                else:
                    st.success("All sample required skills matched!")

        st.caption(
            "These are sample skill-based recommendations, not live "
            "job vacancies or a guarantee of employment."
        )

    # ---------------- RECOMMENDATIONS ----------------
    st.divider()
    st.header("🗺️ Recommended Skills to Learn First")

    graph = build_skill_graph()
    graph.add_nodes_from(result["required"])

    try:
        recommendations = recommend_learning_path(
            result["current"],
            result["missing"]
        )

        if recommendations:
            st.write(
                "Based on the current skill relationship graph, "
                "consider starting with:"
            )
            for skill in recommendations:
                st.write(f"➡️ **{skill}**")
        elif result["missing"]:
            st.info("Review the skill relationships to create a learning path.")
        else:
            st.success("No missing skills in the current sample list!")

    except Exception as error:
        st.warning("Recommendations could not be generated.")
        st.caption(f"Technical details: {error}")

    # ---------------- INTERACTIVE GRAPH ----------------
    st.divider()
    st.header("🕸️ Interactive Skill Graph")

    st.write(
        "Each node represents a skill. Arrows show prerequisite relationships. "
        "Green nodes are skills you selected, orange nodes are missing "
        "skills for your target career, and blue nodes are other connected skills."
    )

    # Keep career-relevant skills plus their direct graph neighbours.
    relevant = set(result["required"]) | set(result["current"])

    for skill in list(relevant):
        if skill in graph:
            relevant.update(graph.predecessors(skill))
            relevant.update(graph.successors(skill))

    subgraph = graph.subgraph(relevant).copy()

    if len(subgraph.nodes) > 0:
        try:
            positions = __import__("networkx").spring_layout(
                subgraph,
                seed=42,
                k=1.1
            )

            edge_x = []
            edge_y = []

            for source, target in subgraph.edges():
                x0, y0 = positions[source]
                x1, y1 = positions[target]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=1.5, color="#9CA3AF"),
                hoverinfo="none"
            )

            node_x = []
            node_y = []
            node_text = []
            node_colors = []

            for skill in subgraph.nodes():
                x, y = positions[skill]
                node_x.append(x)
                node_y.append(y)
                node_text.append(skill)

                if skill in result["current"]:
                    node_colors.append("#16A34A")
                elif skill in result["missing"]:
                    node_colors.append("#F59E0B")
                else:
                    node_colors.append("#3B82F6")

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=node_text,
                textposition="top center",
                hovertemplate="%{text}<extra></extra>",
                marker=dict(
                    size=22,
                    color=node_colors,
                    line=dict(width=1.5, color="white")
                )
            )

            fig = go.Figure(data=[edge_trace, node_trace])

            # Draw arrowheads on the prerequisite edges.
            for source, target in subgraph.edges():
                x0, y0 = positions[source]
                x1, y1 = positions[target]

                fig.add_annotation(
                    x=x1,
                    y=y1,
                    ax=x0,
                    ay=y0,
                    xref="x",
                    yref="y",
                    axref="x",
                    ayref="y",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1.2,
                    arrowcolor="#9CA3AF",
                    standoff=12,
                    startstandoff=12
                )

            fig.update_layout(
                height=600,
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                hovermode="closest"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                "🟢 **Green:** Skills you have  ·  "
                "🟠 **Orange:** Missing career skills  ·  "
                "🔵 **Blue:** Other connected skills"
            )

        except Exception as error:
            st.warning("The graph could not be displayed.")
            st.caption(f"Technical details: {error}")

    st.caption(
        "Prototype note: the career match percentage compares selected skills "
        "with our sample career requirements. It is not a hiring probability "
        "or a validated job-readiness score. Graph recommendations depend "
        "on the current sample relationships."
    )