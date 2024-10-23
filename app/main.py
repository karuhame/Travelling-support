from fastapi import FastAPI
from blog import models
from blog.database import engine, create_sample_data, delete_all
from blog.routers import blog, user, authentication, userInfo, city, review, destination
from fastapi.middleware.cors import CORSMiddleware

        
app = FastAPI()

# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Địa chỉ của ứng dụng Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# def startup_event():
# #     # delete_all(engine=engine)
    
#     models.Base.metadata.drop_all(bind=engine)
#     models.Base.metadata.create_all(engine)
#     create_sample_data() 

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(userInfo.router)
app.include_router(city.router)
app.include_router(review.router)
app.include_router(destination.router)



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
