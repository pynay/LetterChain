import argparse
from langgraph_flow import app_graph  

parser = argparse.ArgumentParser()
parser.add_argument("--resume", required=True)
parser.add_argument("--job", required=True)
parser.add_argument("--tone", default="formal")
args = parser.parse_args()

with open(args.resume, "r") as f:
    resume_text = f.read()

with open(args.job, "r") as f:
    job_text = f.read()

initial_state = {
    "resume_posting": resume_text,
    "job_posting": job_text,
    "tone": args.tone
}

result = app_graph.invoke(initial_state)
print(result["cover_letter"])
