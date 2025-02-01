
MODELS= {
    "embedder": {
        "model": "text-embedding-nomic-embed-text-v1.5"
        },
    "summarizer": {
        "model": "deepseek-r1-distill-llama-8b",
        "max_tokens": 1500,
        "temperature": 0,
        "stream": False
        },
    "emailer": {
        "model": "deepseek-r1-distill-llama-8b",
        "max_tokens": 1500,
        "temperature": 0.3,
        "stream": False
        },
}

MAP_OF_KEYS_CANDIDATE2JOB = {
    "job_title": "job_title",
    "preferred_start_date": "priority_start_date_time",
    "backgrounds": "backgrounds",
    "experiences": "experiences",
    "locations": "provinces",
    "roles": "roles",
    "sectors": "roles",
    "ral_range": "ral_ranges",
}

CLIENT = {
    "base_url": "http://localhost:1234/v1",
    "api_key": "not-needed"
}

DIRECTORIES = {
    "dirty_data": "files",
    "clean_data": "files_cleaned",
    "processed_data": "files_processed",
    "embeddings": "embeddings",
    "matches": "matches"
}

KEYS_TO_KEEP = {
    "job": ["job_id", "apply_type", "platform_url", "status", "published_date_time", "removed_date_time", "updated_date_time", "priority_factor", "priority_end_date_time", "employer_id"],
    "candidate": ["jobseeker_id"]
}

PROMPTS = {
    "initial_candidate_profile": lambda candidate, conversation : f"""
**Task**: 
Extract key information from the following to generate a semi-structured profile of the candidate, make assumptions if needed.

**Input**: 
The candidate's information already known are here: 
{str(candidate)}.

The conversation with the candidate is here:
{str(conversation)}.

**Output Format**:
Return the extracted information in JSON format with the following fields:
- **job_title**: [list of possible job titles]
-**roles**:[list of possible roles]
- **backgrounds**: [list of possible backgrounds]
- **experiences**: [list of possible year of experience]
- **locations**: [list of possible geographic areas (not only cities) where the candidate want to work]
- **preferred_start_date**: [list of preferred start dates]
- **ral_range**: [list of preferred salary ranges]
""",
    "advanced_candidate_profile": lambda candidate: f"""**Task**: Extract key information from the following candidate's json file to create a semi-structured profile of the candidate. Focus on fields that will help match the candidate with job opportunities.

**Input**: Candidate's json file: {str(candidate)}.

**Output Format**: Return the extracted information in JSON format with the following fields:
- **personal_info**: { "first_name", "last_name", "email", "province", "country", "phone_number" }
- **job_search_status**: { "status", "relocation_availability" }
- **job_preferences**: {"preferred_roles", "preferred_sectors", "preferred_locations", "remote_work_preference", "admired_companies" , "salary_expectation" }
- **backgrounds**: {"education_experience", "education_level", "highest_degree_title", "certifications", "professional_experience", "experience_level", "graduation_date", "university" }
- **skills**: { "soft_skills", "hard_skills" }
- **application_history**: [list of companies and roles applied to]
- **interview_statuses**: [list of companies, roles and status of interviews]
- **additional_notes**: { "notes" }

**Instructions**:
1. Extract explicit information from the conversation.
2. Infer implicit information (e.g., soft skills, preferences) based on the context.
3. If a field is not mentioned, leave it as an empty string or an empty list."
""",
    "advanced_job_profile": lambda job: f"""
**Task**: Extract key information from the following job description to create a semi-structured profile of the job. Focus on fields that will help match the job with potential candidates.

**Input**: Job description: {str(job)}.

**Output Format**: Return the extracted information in JSON format with the following fields:
- **job_title**: { "title" }
- **company**: { "name" }
- **location**: { "city", "province", "country", "remote_availability" }
- **job_type**: { "type" }
- **skills_requirements**: { "hard_skills", "soft_skills" }
- **backgrounds_requirements**: {"education_experience", "education_level", "highest_degree_title", "certifications", "professional_experience", "experience_level", "graduation_date", "university" }
- **roles**: [list of relevant roles]
- **sectors**: [list of relevant sectors]
- **key_responsibilities**: [list of responsibilities]
- **benefits**: [list of benefits]
- **additional_notes**: { "notes" }
- **ral_range**: { "min_salary", "max_salary" }
- **priority_start_date_time**: { "date" }

**Instructions**:
1. Extract explicit information from the job description.
2. Infer implicit information (e.g., required soft skills) based on the context.
3. If a field is not mentioned, leave it as an empty string or an empty list.
""",
    "email": lambda candidate, conversation, jobs: f"""you are Matteo and you are helping a candidate (Andrea) via email, in finding the best job for him. 
Below, I will provide the candidate’s profile, your past email conversation, and some new job opportunities for you to suggest. 

Please craft a response that follows the flow of the conversation, maintaining the same tone and length, be kind and friendly and naturally introduce the new positions listed below. If relevant, you can ask the candidate for additional informations, or updates.

When listing the new jobs, follow the same format as in previous emails: typically the title, a very brief description, and the job link. Ensure the response style matches the previous ones.

**Candidate Profile**:
{candidate}

**Past Email Conversation**:
{conversation}

**New Job Opportunities (Format: Title, Brief Description, Link)**:
{jobs}
"""
}
