from fastapi import FastAPI, HTTPException
from schemas import (
    LoginRequest, RegisterRequest, ChangePasswordRequest, UpdateProfileRequest,
    FoodLogRequest, FoodUpdateRequest, FoodDeleteRequest,
    ArticleCreateRequest, ArticleUpdateRequest, ArticleDeleteRequest,
    SaveArticleRequest, DeleteSavedArticleRequest,
    PostCreateRequest, PostUpdateContentRequest, PostUpdateAudienceRequest,
    PostUpdateImageRequest, PostDeleteRequest,
    SaveUserExercisesRequest, SaveExerciseRequest, RemoveSavedExerciseRequest,
    CreateChatRequest, SaveMessageRequest, DeleteMessageRequest, DeleteAllMessagesRequest
)
from my_connector import AuthTbl
import base64

app = FastAPI()
auth = AuthTbl()


def decode_base64_image(b64: str):
    if not b64:
        return None
    if "," in b64:
        b64 = b64.split(",")[1]
    return base64.b64decode(b64)


# ---------------- AUTH ----------------
@app.post("/auth/login")
def login(data: LoginRequest):
    user_id = auth.check_password(data.username, data.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    try:
        auth.update_last_login(user_id)
    except Exception:
        pass
    return {"user_id": user_id}


@app.post("/auth/register")
def register(data: RegisterRequest):
    try:
        photo_bytes = decode_base64_image(data.photo_base64) if data.photo_base64 else None
        user_id, bmi, bmi_status, daily_goal = auth.insert_info(
            username=data.username,
            email=data.email,
            password=data.password,
            fullname=data.fullname,
            age=data.age,
            gender=data.gender,
            height=data.height,
            weight=data.weight,
            goal=data.goal,
            activity=data.activity,
            desired_weight=data.desired_weight,
            has_health_condition=data.has_health_condition,
            specific_condition=data.specific_condition,
            photo_bytes=photo_bytes
        )
        return {
            "user_id": user_id,
            "bmi": bmi,
            "bmi_status": bmi_status,
            "daily_goal": daily_goal
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/change-password")
def change_password(data: ChangePasswordRequest):
    if not auth.verify_user_password(data.user_id, data.old_password):
        raise HTTPException(status_code=401, detail="Old password is incorrect")
    ok = auth.update_password(data.user_id, data.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to update password")
    return {"updated": True}


@app.put("/user/profile")
def update_profile(data: UpdateProfileRequest):
    ok = auth.update_user_profile(
        user_id=data.user_id,
        username=data.username,
        fullname=data.fullname,
        age=data.age,
        gender=data.gender,
        height=data.height,
        weight=data.weight,
        activity=data.activity,
        has_condition=data.has_condition,
        condition=data.condition
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to update profile")
    return {"updated": True}


@app.get("/user/profile")
def get_user_profile(user_id: int):
    info = auth.get_user_profile_info(user_id)
    if not info:
        raise HTTPException(status_code=404, detail="User not found")
    return info


# ---------------- FOOD ----------------
@app.post("/food")
def add_food(data: FoodLogRequest):
    food_id = auth.insert_food(
        user_id=data.user_id,
        food_name=data.food_name,
        quantity=data.quantity,
        meal_category=data.meal_category,
        calories=data.calories
    )
    if not food_id:
        raise HTTPException(status_code=400, detail="Failed to insert food")
    return {"food_id": food_id}


@app.put("/food")
def update_food(data: FoodUpdateRequest):
    payload = {
        "FoodId": data.food_id,
        "FoodName": data.food_name,
        "FoodQuantity": data.quantity,
        "MealCategory": data.meal_category,
        "Calories": data.calories
    }
    ok = auth.update_food_entry_by_id(payload)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to update food")
    return {"updated": True}


@app.delete("/food")
def delete_food(data: FoodDeleteRequest):
    ok = auth.delete_food_entry_by_id(data.food_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to delete food")
    return {"deleted": True}


@app.get("/food")
def get_food_by_date(user_id: int, date: str):
    rows = auth.get_user_food_entries_by_date(user_id, date)
    return {"items": rows or []}


# ---------------- ARTICLES ----------------
@app.post("/articles")
def create_article(data: ArticleCreateRequest):
    ok = auth.add_article_to_db(data.dict())
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to add article")
    return {"created": True}


@app.put("/articles")
def update_article(data: ArticleUpdateRequest):
    ok = auth.update_article(data.article_id, data.dict())
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to update article")
    return {"updated": True}


@app.delete("/articles")
def delete_article(data: ArticleDeleteRequest):
    ok = auth.delete_article(data.article_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to delete article")
    return {"deleted": True}


@app.get("/articles")
def get_all_articles():
    return {"items": auth.get_all_articles()}


@app.post("/saved-articles")
def save_article(data: SaveArticleRequest):
    article = {
        "ArticleId": data.article_id,
        "category": data.category,
        "title": data.title,
        "author": data.author,
        "date": data.date,
        "body": data.body,
        "image": data.image
    }
    ok = auth.save_article(data.user_id, article)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to save article")
    return {"saved": True}


@app.get("/saved-articles")
def get_saved_articles(user_id: int):
    return {"items": auth.get_saved_articles(user_id)}


@app.delete("/saved-articles")
def delete_saved_article(data: DeleteSavedArticleRequest):
    ok = auth.delete_saved_article(data.saved_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to delete saved article")
    return {"deleted": True}


# ---------------- POSTS ----------------
@app.post("/posts")
def create_post(data: PostCreateRequest):
    img = decode_base64_image(data.post_image_base64) if data.post_image_base64 else None
    post_id = auth.create_post(data.user_id, data.text, img, data.audience)
    if not post_id:
        raise HTTPException(status_code=400, detail="Failed to create post")
    return {"post_id": post_id}


@app.get("/posts/all")
def get_all_posts():
    return {"items": auth.get_all_posts()}


@app.get("/posts/user")
def get_posts_by_user(user_id: int):
    return {"items": auth.get_user_posts(user_id)}


@app.get("/posts")
def get_post_by_id(post_id: int):
    post = auth.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.get("/posts/by-date")
def get_posts_by_user_and_date(user_id: int, date: str):
    return {"items": auth.get_posts_by_user_and_date(user_id, date)}


@app.put("/posts/content")
def update_post_content(data: PostUpdateContentRequest):
    ok = auth.update_post_content(data.post_id, data.text)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to update post")
    return {"updated": True}


@app.put("/posts/audience")
def update_post_audience(data: PostUpdateAudienceRequest):
    ok = auth.update_post_audience(data.post_id, data.audience)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to update audience")
    return {"updated": True}


@app.put("/posts/image")
def update_post_image(data: PostUpdateImageRequest):
    img = decode_base64_image(data.post_image_base64)
    ok = auth.update_post_image(data.post_id, img)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to update post image")
    return {"updated": True}


@app.delete("/posts")
def delete_post(data: PostDeleteRequest):
    ok = auth.delete_post(data.post_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to delete post")
    return {"deleted": True}


# ---------------- EXERCISES ----------------
@app.post("/user-exercises")
def save_user_exercises(data: SaveUserExercisesRequest):
    try:
        auth.save_user_exercises(
            user_id=data.user_id,
            exercises=[ex.dict() for ex in data.exercises],
            goal=data.goal,
            difficulty=data.difficulty,
            mode=data.mode
        )
        return {"saved": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/saved-exercises")
def save_exercise(data: SaveExerciseRequest):
    ok = auth.add_saved_exercise(
        user_id=data.user_id,
        ex=data.exercise.dict(),
        program_name=data.program_name,
        user_exercise_id=data.user_exercise_id
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to save exercise")
    return {"saved": True}


@app.get("/saved-exercises")
def get_saved_exercises(user_id: int):
    return {"items": auth.get_saved_exercises(user_id)}


@app.delete("/saved-exercises")
def remove_saved_exercise(data: RemoveSavedExerciseRequest):
    ok = auth.remove_saved_exercise(data.user_id, data.name)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to remove exercise")
    return {"deleted": True}


# ---------------- AI ----------------
@app.post("/ai/chats")
def create_or_get_chat(data: CreateChatRequest):
    chat_id = auth.get_or_create_chat(data.user_id)
    if not chat_id:
        raise HTTPException(status_code=400, detail="Failed to create chat")
    return {"chat_id": chat_id}


@app.post("/ai/messages")
def save_message(data: SaveMessageRequest):
    message_id = auth.save_message(data.chat_id, data.role, data.content)
    if not message_id:
        raise HTTPException(status_code=400, detail="Failed to save message")
    return {"message_id": message_id}


@app.get("/ai/messages")
def get_chat_messages(chat_id: int, user_id: int):
    return {"items": auth.get_chat_messages(chat_id, user_id)}


@app.get("/ai/messages/search")
def search_messages(chat_id: int, query: str):
    return {"items": auth.search_messages(chat_id, query)}


@app.delete("/ai/messages")
def delete_message(data: DeleteMessageRequest):
    ok = auth.delete_message(data.message_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to delete message")
    return {"deleted": True}


@app.delete("/ai/messages/all")
def delete_all_messages(data: DeleteAllMessagesRequest):
    ok = auth.delete_all_messages(data.chat_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to delete all messages")
    return {"deleted": True}