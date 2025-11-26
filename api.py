from fastapi import FastAPI

app = FastAPI();

@app.get("/")
async def root():
	return {
		"welcome_message": "Methods available",
			"methods": [
				{"change_outline": "http://localhost:8000/api/v1/methods/change_outline"},
				{"receive_result": "http://localhost:8000/api/v1/methods/receive_result"}
			]
	}

@app.get("/api/v1/methods/change_outline")
async def burgers():
	return{
		"outline_id":"num",
		"new_outline":"text"
	}

@app.get("/api/v1/methods/receive_result")
async def sandwiches():
	return{
		"outline_id":"num",
		"new_text":"lots of data data data date"
	}
