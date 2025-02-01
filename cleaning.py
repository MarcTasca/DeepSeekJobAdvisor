from config import DIRECTORIES
from utils import parse_html, parse_email, extract_context
import os, json

class JobCleaner():
    """This class is responsible for selecting jobs that are available and not already seen by the candidate.
    Clean them and eventually save them to the right path.
    """
    def __init__(self):
        self.source = DIRECTORIES["dirty_data"]
        self.dest = DIRECTORIES["clean_data"]
        
        # load job_data
        with open (os.path.join(self.source, "job_data.json"), 'r') as file:
            self.jobs = json.load(file)

        # load job_views
        with open (os.path.join(self.source, "job_views.json"), 'r') as file:
            self.job_views = json.load(file)

    def merge_jobs2job_views(self):
        """Merge jobs and job_views creating a new field in jobs: viewed: bool
        """
        # merge jobs and job_views creating a new field in jobs: viewed: bool
        job_views_ids = set([job_view["job_id"] for job_view in self.job_views])
        for job in self.jobs:
            job["viewed"] = True if job["job_id"] in job_views_ids else False
        
        return self.jobs

    def select(self, status = "publish", viewed = False):
        """Select jobs that are available and not already seen by the candidate.
        Args:
        status (str): The status of the job. Default is "publish".
        viewed (bool): Whether the job has been viewed by the candidate. Default is False.
        """
        self.selected_jobs = []
        for job in self.jobs:
            if job["status"] == status and job["viewed"] == viewed:
                self.selected_jobs.append(job)

        return self.selected_jobs

    def clean(self):
        """Clean the selected jobs.
        """
        for job in self.selected_jobs:
            job['job_description'] = parse_html(job['content_html'])
            del job['content_html']

        return self.selected_jobs

    def save(self):
        """Save the selected jobs to the right path.
        """
        os.makedirs(self.dest, exist_ok=True)
        with open(os.path.join(self.dest, "job_data.json"), 'w') as file:
            json.dump(self.selected_jobs, file, indent=4)

    def run(self):
        """Run the cleaner:
        - Merge jobs and job_views
        - filter jobs (based on status and viewed)
        - Clean jobs (parse html of description)
        - Save filtered jobs
        """
        self.merge_jobs2job_views()
        self.select()
        self.clean()
        self.save()


class ConversationCleaner():
    """This class is responsible for cleaning the conversation between the candidate and the employer.
    Clean them and eventually save them to the right path.
    """
    def __init__(self):
        self.source = DIRECTORIES["dirty_data"]
        self.dest = DIRECTORIES["clean_data"]

        with open(os.path.join(self.source, "conversation.json")) as file:
            self.conversation = json.load(file)
        
    def clean(self):
        """Clean the conversation:
        - sort it by date
        - save the context: what happened before the first message
        - from the second oldest, parse the email body
        """
        # sort it by date
        self.conversation = sorted(self.conversation, key=lambda x: x['send_date_time'])

        # save the context: what happened before the first message
        self.context = extract_context(self.conversation[0]['body'])

        # from the second oldest, parse the email body
        for email in self.conversation:
            email['body'] = parse_email(email['body'])

        return self.conversation, self.context

    def save(self):
        """Save the cleaned conversation and context to the right path.
        """
        os.makedirs(self.dest, exist_ok=True)

        with open (os.path.join(self.dest, "conversation.json"), 'w') as f:
            json.dump(self.conversation, f, indent=4)

        with open (os.path.join(self.dest, 'context.json'), 'w') as f:
            json.dump(self.context, f, indent=4)

    def run(self):
        """Run the cleaner:
        - Clean the conversation
        - Save the cleaned conversation
        """
        self.clean()
        self.save()
