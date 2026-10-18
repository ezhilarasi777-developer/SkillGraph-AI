import networkx as nx


def build_skill_graph():
    graph = nx.DiGraph()

    skill_paths = [
        ("Python", "Pandas"),
        ("Python", "NumPy"),
        ("Python", "Data Structures"),
        ("Data Structures", "Algorithms"),
        ("Algorithms", "Machine Learning"),
        ("Statistics", "Machine Learning"),
        ("NumPy", "Pandas"),
        ("NumPy", "Machine Learning"),
        ("Pandas", "Data Analysis"),
        ("SQL", "Data Analysis"),
        ("Data Analysis", "Data Visualization"),
        ("Data Visualization", "Machine Learning"),
        ("Machine Learning", "Deep Learning"),
        ("HTML", "CSS"),
        ("CSS", "JavaScript"),
        ("JavaScript", "React"),
        ("Python", "Flask"),
        ("SQL", "Flask"),
        ("Linux", "Cloud Computing"),
        ("Networking", "Cloud Computing"),
        ("Git and GitHub", "Cloud Computing"),
        ("C++", "Data Structures"),
    ]

    graph.add_edges_from(skill_paths)
    return graph


def recommend_learning_path(current_skills, missing_skills):
    graph = build_skill_graph()

    current = set(current_skills)
    missing = set(missing_skills)

    graph.add_nodes_from(current | missing)

    recommendations = []
    remaining = set(missing)

    # Recommend skills in prerequisite order.
    while remaining:
        ready = []

        for skill in remaining:
            prerequisites = list(graph.predecessors(skill))

            if all(
                prerequisite in current
                or prerequisite not in remaining
                for prerequisite in prerequisites
            ):
                ready.append(skill)

        if not ready:
            # Avoid getting stuck if the graph has incomplete
            # dependency information.
            ready = sorted(remaining)

        ready.sort()

        for skill in ready:
            recommendations.append(skill)
            remaining.remove(skill)

    return recommendations