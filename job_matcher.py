from job_data import JOB_ROLES


def recommend_jobs(current_skills):
    current = set(current_skills)
    job_matches = []

    for job_title, required_skills in JOB_ROLES.items():
        required = set(required_skills)

        matched = sorted(current & required)
        missing = sorted(required - current)

        percentage = round(
            len(matched) / len(required) * 100
        ) if required else 0

        job_matches.append({
            "job_title": job_title,
            "percentage": percentage,
            "matched": matched,
            "missing": missing
        })

    # Highest skill match first
    job_matches.sort(
        key=lambda job: (
            -job["percentage"],
            len(job["missing"]),
            job["job_title"]
        )
    )

    return job_matches