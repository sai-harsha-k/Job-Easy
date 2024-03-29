def create_inverted_index(jobs):
    inverted_index = {}
    for job in jobs:
        job_skills = job.skills.split(',')  # Assuming skills are stored as a comma-separated string
        for skill in job_skills:
            skill = skill.strip().lower()
            if skill not in inverted_index:
                inverted_index[skill] = set()
            inverted_index[skill].add(job.job_id)  # Use job.job_id instead of job.id
    return inverted_index
