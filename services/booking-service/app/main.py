from fastapi import FastAPI
app = FastAPI(title="Booking Service")
@app.get("/")
def home():
	return {"message": "Booking Service Running"}

