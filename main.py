from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from uuid import uuid4

app = FastAPI()

# In-memory database to store users and posts (for demonstration purposes)
users_db = {}
posts_db = {}

# Pydantic model for User data (for registration and authentication)
class User(BaseModel):
    username: str  # Username of the user
    password: str  # Password for the user

# Pydantic model for Post data
class Post(BaseModel):
    content: str  # Content of the post
    username: str  # Username of the post creator

# Pydantic model for a User with ID (used internally after registration)
class UserInDB(User):
    id: str  # Unique ID for each user in the database

# Utility function to simulate user authentication
def authenticate_user(username: str, password: str) -> UserInDB:
    """
    Authenticate a user based on username and password.
    Checks if the username exists and if the password matches.
    """
    if username in users_db and users_db[username]["password"] == password:
        return UserInDB(id=users_db[username]["id"], username=username, password=password)
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Route for user registration
@app.post("/register", response_model=UserInDB)
def register(user: User):
    """
    Register a new user by providing a username and password.
    Returns the user details along with a unique ID.
    """
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Generate a unique user ID
    user_id = str(uuid4())  # Use uuid4 to generate a random unique ID
    users_db[user.username] = {"id": user_id, "password": user.password}
    
    # Return the registered user information
    return UserInDB(id=user_id, username=user.username, password=user.password)

# Route for user login (simple authentication check)
@app.post("/login")
def login(user: User):
    """
    Login a user by providing their username and password.
    Authenticates the user, and returns a welcome message if successful.
    """
    authenticate_user(user.username, user.password)  # Authenticate the user
    return {"message": f"Welcome, {user.username}!"}  # Return a welcome message if successful

# Route for creating a new post
@app.post("/posts", response_model=Post)
def create_post(post: Post):
    """
    Create a new post. A post requires content and a username (of the creator).
    The username must exist in the database.
    """
    # Check if the username exists in the users_db
    if post.username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    # Retrieve the user_id using the username
    user_id = users_db[post.username]["id"]
    
    # Generate a unique post ID and set the timestamp for the post
    post_id = str(uuid4())
    created_at = datetime.now()
    
    # Save the post in the database
    posts_db[post_id] = {"content": post.content, "username": post.username, "created_at": created_at}
    
    # Return the created post
    return {**post.dict(), "created_at": created_at}

# Route for fetching all posts
@app.get("/posts", response_model=List[Post])
def get_posts():
    """
    Get all posts from the database.
    Returns a list of posts with user ID, content, and creation time.
    """
    # Convert each post from dictionary format to Post model and return the list
    return [
        Post(content=post["content"], username=post["username"])
        for post in posts_db.values()
    ]

# Run the application: uvicorn filename:app --reload
