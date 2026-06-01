from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "MUN Delegate Management Portal"}
