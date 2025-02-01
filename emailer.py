from typing import List, Dict, Callable
from config import DIRECTORIES, PROMPTS, MODELS, CLIENT
import json, os
from utils import email_response
from openai import OpenAI

class EmailMaker:
    """
    This class generates job suggestion emails based on candidate scores and conversation history.
    """

    def __init__(self):
        self.client = OpenAI(api_key=CLIENT["api_key"], base_url=CLIENT["base_url"])
        self.source_jobs = DIRECTORIES["processed_data"]
        self.source_candidate = DIRECTORIES["dirty_data"]
        self.source_conversation = DIRECTORIES["clean_data"]
        self.model = MODELS["emailer"]
        self.prompt = PROMPTS["email"]

        # load job data
        with open(os.path.join(self.source_jobs, "job_data.json"), "r") as f:
            self.jobs = json.load(f)

        # load candidate data
        with open(os.path.join(self.source_candidate, "jobseeker.json"), "r") as f:
            self.candidate = json.load(f)

        # load conversation data
        with open(os.path.join(self.source_conversation, "conversation.json"), "r") as f:
            self.conversation = json.load(f)
        self.conversation = ("\n---\n").join([f"Sender: {msg['sender']}\n{msg['body']}" for msg in self.conversation])

    def suggest_jobs(self, jobs: List[Dict] = None) -> List[Dict]:
        if jobs is None:
            jobs = self.jobs
        
        # Sort jobs based on score and select the first 3
        sorted_jobs = sorted(jobs, key=lambda x: x['score'], reverse=True)
        self.suggested_jobs = sorted_jobs[:2]

        for job in self.suggested_jobs:
            del job["job_description"]
        return self.suggested_jobs

    def generate_email(self, client: OpenAI=None, candidate: str=None, conversation: str=None, suggested_jobs: List[Dict]=None, prompt: Callable=None) -> str:
        if client is None:
            client = self.client

        if candidate is None:
            candidate = self.candidate

        if conversation is None:
            conversation = self.conversation

        if suggested_jobs is None:
            suggested_jobs = self.suggested_jobs
        
        if prompt is None:
            prompt = self.prompt
        
        prompt = prompt(str(candidate), str(conversation), str(suggested_jobs))

        self.answer = email_response(client, prompt, **self.model)

        return self.answer