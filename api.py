from fastapi import FastAPI
import uvicorn

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
		"outline_count":"num",
		"new_text":"""
A knight and a peasant were best friends. But then the peasant slept with the princess and the knight is ordered to kill his friend.
The Knight must go on a treacherous journey to kill his friend or put his family and himself in danger.
The knight finds his friend, disheveled and weak. He decides against killing his best friend
The king hears that the knight failed to do his duty. He comes home to his family, slaughtered!
The knight, filled with hatred and revenge, finds his friend and kills him in front of the king!
"""
	}

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000) #might need to change 0.0.0.0 to 127.0.0.1
