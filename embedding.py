import json
import itertools
from openai import OpenAI
from tqdm import tqdm
import numpy as np
from tqdm import tqdm
import numpy as np
import os
import pickle

from config import CLIENT, DIRECTORIES, MODELS, PROMPTS, MAP_OF_KEYS_CANDIDATE2JOB
from utils import go_get_jason, get_embedding
from sklearn.metrics.pairwise import cosine_similarity


class JobEmbedder():
    def __init__(self):
        self.client = OpenAI(api_key=CLIENT["api_key"], base_url=CLIENT["base_url"])
        self.source = DIRECTORIES["clean_data"]
        self.dest_embeddings = DIRECTORIES["embeddings"]
        self.model = MODELS["embedder"]

        # load the jobs and convert them to a dictionary
        with open(f"{self.source}/job_data.json", "r") as f:
            self.jobs = json.load(f)
        self.jobs = {job["job_id"]: job for job in self.jobs}
    
    def embed(self):
        self.job_embeddings = {}

        # keys to keep:
        keys2keep = ['job_title', 'priority_start_date_time', 'backgrounds', 'experiences', 'provinces', 'roles', 'sectors', 'ral_ranges']

        # get the embedding for each key2keep
        for key, job in tqdm(self.jobs.items()):
            job_embedding = {k: get_embedding(self.client, self.model["model"], str(v)) for k, v in job.items() if k in keys2keep}
            self.job_embeddings[key] = job_embedding

        return self.job_embeddings
    
    def save(self):
        os.makedirs(self.dest_embeddings, exist_ok=True)
        with open(os.path.join(self.dest_embeddings, "job_embeddings.pkl"), 'wb') as f:
            pickle.dump(self.job_embeddings, f)

    def run(self):
        print("Embedding the jobs ...")
        self.embed()

        print("Saving the job embeddings ...")
        self.save()

        print(f"Jobs embedded and saved: {len(self.job_embeddings)}")
        return self.job_embeddings
    

class CandidateEmbedder():
    def __init__(self):
        self.client = OpenAI(api_key=CLIENT["api_key"], base_url=CLIENT["base_url"])
        self.source_candidate = DIRECTORIES["dirty_data"]
        self.source_conversation = DIRECTORIES["clean_data"]
        self.dest_embeddings = DIRECTORIES["embeddings"]
        self.model_summarizer = MODELS["summarizer"]
        self.model_embedder = MODELS["embedder"]

        # load the candidate and the conversation
        with open(os.path.join(self.source_candidate, "jobseeker.json"), "r") as f:
            self.candidate = json.load(f)
        with open(os.path.join(self.source_conversation, "conversation.json"), "r") as f:
            self.conversation = json.load(f)

        # concatenate the conversation
        self.conversation = ("---").join([msg["body"] for msg in self.conversation])

    def extract_candidate_profile(self):
        # Generate the prompt
        prompt = PROMPTS["initial_candidate_profile"]
        prompt = prompt(self.candidate, self.conversation)

        # Get the candidate profile, asking the model to summarize the conversation and the candidate profile
        _, self.candidate_profile = go_get_jason(self.client, prompt, **self.model_summarizer)        
        return self.candidate_profile
    
    def generate_combinations(self, candidate_profile=None):
        if candidate_profile is None:
            candidate_profile = self.candidate_profile

        # Get the keys and values from the input dictionary
        keys, values = zip(*candidate_profile.items())

        # Generate all possible combinations of the values
        self.candidate_profiles = [dict(zip(keys, combination)) for combination in itertools.product(*values)]
        return self.candidate_profiles
    
    def embed(self):
        # Embed the candidate profiles
        candidate_embeddings = []
        for profile in tqdm(self.candidate_profiles):
            candidate_embedding = {}

            for key, value in profile.items():
                candidate_embedding[key] = get_embedding(self.client, self.model_embedder["model"], str(value))
            candidate_embeddings.append(candidate_embedding)

        return candidate_embeddings
    
    def save(self):
        os.makedirs(self.dest_embeddings, exist_ok=True)
        with open(os.path.join(self.dest_embeddings, "candidate_embeddings.pkl"), 'wb') as f:
            pickle.dump(self.candidate_embeddings, f)

    def run(self):
        print(f"Run moodel {self.model_summarizer['model']} to extract candidate profile")
        self.candidate_profile = self.extract_candidate_profile()
        print(f"Candidate profile extracted: {self.candidate_profile}")
        
        print("Generate all possible combinations of the candidate profile with model ", self.model_embedder["model"])
        self.candidate_profiles = self.generate_combinations()
        self.candidate_embeddings = self.embed()

        print("Save the candidate embeddings")
        self.save()

        print(f"Candidate embeddings saved: {len(self.candidate_embeddings)}")
        return self.candidate_embeddings


class ScoreCalculator():
    """This class is responsible for calculating the score of each job for each candidate.
    """
    def __init__(self):
        self.source_embeddings = DIRECTORIES["embeddings"]
        self.source_jobs = DIRECTORIES["clean_data"]
        self.dest_matching = DIRECTORIES["matches"]
        self.dest_processed = DIRECTORIES["processed_data"]
        self.map = MAP_OF_KEYS_CANDIDATE2JOB

        print("Loading the job embeddings ...")
        with open(os.path.join(self.source_embeddings, "job_embeddings.pkl"), "rb") as f:
            self.job_embeddings = pickle.load(f)
        print(len(self.job_embeddings), type(self.job_embeddings))

        print("Loading the candidate embeddings ...")
        with open(os.path.join(self.source_embeddings, "candidate_embeddings.pkl"), "rb") as f:
            self.candidate_embeddings = pickle.load(f)
        print(len(self.candidate_embeddings), type(self.candidate_embeddings))

        print("Loading the jobs ...")
        with open(os.path.join(self.source_jobs, "job_data.json"), "r") as f:
            self.jobs = json.load(f)
        print(len(self.jobs), type(self.jobs))
    
    def calculate(self, map=None):
        if map is None:
            map = self.map

        map_reverse = {v: k for k, v in map.items()}

        candidate_embeddings_matrix = np.vstack([np.hstack([c[k] for k in c.keys()]) for c in self.candidate_embeddings])

        job_rank = {}
        for job_id in tqdm(self.job_embeddings.keys()):
            job_embedding = np.hstack([self.job_embeddings[job_id][k] for k in map_reverse.keys()])

            # Compute cosine similarity between job embedding and all candidate embeddings
            similarity_scores = cosine_similarity(candidate_embeddings_matrix, job_embedding.reshape(1, -1))
            job_rank[job_id] = similarity_scores.mean()

        # order the final rank
        self.job_rank = dict(sorted(job_rank.items(), key=lambda item: item[1], reverse=True))
        
        return self.job_rank
    
    def merge_jobs_rank(self, job_rank=None, jobs=None):
        if job_rank is None:
            job_rank = self.job_rank

        if jobs is None:
            jobs = self.jobs
        
        for job in self.jobs:
            job["score"] = job_rank[job["job_id"]]
        
        return self.jobs
    
    def save_rank(self, job_rank=None):
        if job_rank is None:
            job_rank = self.job_rank
        
        os.makedirs(self.dest_matching, exist_ok=True)
        with open(os.path.join(self.dest_matching, "job_rank.pkl"), 'wb') as f:
            pickle.dump(job_rank, f)

    def save_jobs(self, jobs=None):
        if jobs is None:
            jobs = self.jobs

        os.makedirs(self.dest_processed, exist_ok=True)
        with open(os.path.join(self.dest_processed, "job_data.json"), 'w') as f:
            json.dump(jobs, f, indent=4)

    def run(self):
        print("Calculating the score for each job ...")
        self.calculate()
        self.jobs = self.merge_jobs_rank()
        self.save_rank()
        self.save_jobs()
        print(f"Jobs ranked and saved: {len(self.jobs)}")
        return self.jobs