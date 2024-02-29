from dotenv import load_dotenv
import uvicorn
import os
load_dotenv()


def main():
    uvicorn.run(
        "lise_planning_api.internal.app:app", 
        host="0.0.0.0", 
        port=8000, 
        log_level="info", 
        reload=os.getenv("DEBUG", False) == "True",
    )