# General files structure
I have 6 json file to start with: 
- applications.json: a list of application done by Federico
- conversation.json: a list of email between Federico and the recruiter, trying to match him with the right job
- job_data.json: a list of all info about jobs
- job_views.json: a list of the job visualized by the jobseeker
- jobseeker.json: the profile of the jobseeker
- match.json: a list of potential matching with the corresponding score

# objective
The objective of the project is to develop a system that can suggest job opportunities to jobseekers based on these files and write a mail to the jobseeker with the job description and the link to the job page matching the tone and the length of the previous conversation, and aware of the past conversation. 

I decided to do everything in local, by using the new deepseek distilled. In this way the cost is zero. Of course it is easy adaptable to online api, from deepseek it is basically plug and play.

In order to make it run locally you just need to:
- 1. Install LM studio
- 2. Download two models:
    - deepseek-r1-distill-llama-8b
    - text-embedding-nomic-embed-text-v1.5

Moreover you need this libraries installed:


## Frontend
- Make a very simplified frontend. For a PoC, Streamlit should be enough. I will not check all the possible typing errors and stuff <3.
- It should:
    - display jobseeker info, conversation summary, features extracted and past applications.
    - list of potential new applications.
    - the email to send to the jobseeker.

## Cleaning & Storing
- 1. Mails are cleaned in a brutal way, but it seems good enough (for a PoC)
- 2. From job descriptions, I'll use a dedicated library, because they contains a lot of HTML tags and stuff.
- 3. After I want to store all the data in a MongoDB, or something similar (it keeps the json format and allows for freedom in adding  fields), but for now I implemented some very simple classes to process data.

## Feature extraction (candidate)
- For the candidate we do a simple feature extraction based on semi-structured output thank to a personalized prompt (we also tried with the structured output option, but it was not ready for deepseek -and we strongly wanted to use it!!). This retrieves us a list for each attribute, we then create a list with all possible combinations on that list, so we end up having multiple potential candidate from the candidate description.

- We used a model hosted locally, a distilled version of deepseek, on a local server using LM studio (so cool, in this way everything it is fre... and I am unemployed, so that's better)

## Embedding features, selecting jobs
We embedded both candidate and jobs (unviewed by candidate and published) in this way:
- 1. we selected the same attributes from both (mapping them, slightly different names)
- 2. we embedded all the fields separately (using another local hosted model, all info in config.py, maybe the model used is an overkill, we can try others)
- 3. we computed cosine_similarity between fields of corresponding attributes (mapped before), and averaged all the scores ending up with a list containing similarities between jobs and candidate. AT! we have a list of potential candidate profiles (from feature extraction) so we have to do two loops of averaging: **External loop**, over jobs, **internal loop** over candidate profiles.

## Result and conclusions
We take the first job obtained in this way, maybe the first two and we craft the corresponding email, taking into consideration a natural consecutio to the conversation through mail.

We may take into consideration also to make some questions, based on existing empty attributes (but for now we keep it simple).

Finally, this whole may seems as an overkill, but I think it takes into consideration different scenario, and different words, to keep it very stable and do not miss eventual jobs for the candidate. If not, it wouldn't be new. A lot of recommendation system out there are based on words matching that blow away every time a single letter is  missing.


# Future updates
I didn't have the time, but I would love to try and test all of them

## Recommendation System
- We cannot use collaborative filtering (we have only Federico) but we can use content-based filtering, this involve checking the list of applications of the candidate (which is a list we know), understand the requirements and find similar (we could simply embed them and use cosine similarity, but we risk to miss the difference between mandatory requirements and suggestions or bonus (yes no maybe??)).

 - Sto poraccio si chiama Federico, non Andrea, si firma così nella mail! (potrei pensare a un correttore per il profilo del candidato (jobseeker.json))