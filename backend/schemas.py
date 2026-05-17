from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal


# ---------- AUTH ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    fullname: str
    age: int
    gender: str
    height: float
    weight: float
    goal: str
    activity: str
    desired_weight: Optional[float] = None
    has_health_condition: Literal["Yes", "No"]
    specific_condition: Optional[str] = None
    photo_base64: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    user_id: int
    username: str
    fullname: str
    age: int
    gender: str
    height: float
    weight: float
    activity: str
    has_condition: Literal["Yes", "No"]
    condition: Optional[str] = None


# ---------- FOOD ----------
class FoodLogRequest(BaseModel):
    user_id: int
    food_name: str
    quantity: int
    meal_category: str
    calories: float


class FoodUpdateRequest(BaseModel):
    food_id: int
    food_name: str
    quantity: int
    meal_category: str
    calories: float


class FoodDeleteRequest(BaseModel):
    food_id: int


# ---------- ARTICLES ----------
class ArticleCreateRequest(BaseModel):
    category: str
    title: str
    author: str
    date: str
    body: str
    image: Optional[str] = None


class ArticleUpdateRequest(BaseModel):
    article_id: int
    category: str
    title: str
    author: str
    date: str
    body: str
    image: Optional[str] = None


class ArticleDeleteRequest(BaseModel):
    article_id: int


class SaveArticleRequest(BaseModel):
    user_id: int
    article_id: Optional[int] = None
    category: str
    title: str
    author: str
    date: str
    body: str
    image: Optional[str] = None


class DeleteSavedArticleRequest(BaseModel):
    saved_id: int


# ---------- POSTS ----------
class PostCreateRequest(BaseModel):
    user_id: int
    text: str
    audience: Optional[str] = "Public"
    post_image_base64: Optional[str] = None


class PostUpdateContentRequest(BaseModel):
    post_id: int
    text: str


class PostUpdateAudienceRequest(BaseModel):
    post_id: int
    audience: str


class PostUpdateImageRequest(BaseModel):
    post_id: int
    post_image_base64: str


class PostDeleteRequest(BaseModel):
    post_id: int


# ---------- EXERCISES ----------
class ExerciseItem(BaseModel):
    name: str
    sets: int
    reps: int
    rest: int
    meaning: Optional[str] = None
    steps: Optional[str] = None
    benefits: Optional[str] = None


class SaveUserExercisesRequest(BaseModel):
    user_id: int
    goal: str
    difficulty: str
    mode: str
    exercises: List[ExerciseItem]


class SaveExerciseRequest(BaseModel):
    user_id: int
    program_name: str
    exercise: ExerciseItem
    user_exercise_id: Optional[int] = None


class RemoveSavedExerciseRequest(BaseModel):
    user_id: int
    name: str


# ---------- AI ----------
class CreateChatRequest(BaseModel):
    user_id: int


class SaveMessageRequest(BaseModel):
    chat_id: int
    role: Literal["user", "assistant"]
    content: str


class DeleteMessageRequest(BaseModel):
    message_id: int


class DeleteAllMessagesRequest(BaseModel):
    chat_id: int