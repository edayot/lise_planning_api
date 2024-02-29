import uvicorn


def main():
    uvicorn.run("lise_planning_api.internal.app:app", host="localhost", port=8000, log_level="info", reload=True)