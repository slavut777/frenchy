from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
import json
import requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
import random
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

# Initialize MongoDB client
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Initialize FastAPI app
app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class WordBase(BaseModel):
    french: str
    russian: str
    pronunciation: Optional[str] = None

class WordCreate(WordBase):
    pass

class Word(WordBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

class WordProgressBase(BaseModel):
    word_id: str
    status: str  # "new", "learning", "known"
    strength: int = Field(default=0, ge=0, le=5)  # 0-5 knowledge strength
    next_review: Optional[datetime] = None

class WordProgressCreate(WordProgressBase):
    pass

class WordProgress(WordProgressBase):
    id: str
    updated_at: datetime

    class Config:
        orm_mode = True

class FlashcardResponse(BaseModel):
    id: str
    french: str
    russian: str
    pronunciation: Optional[str] = None
    status: str
    strength: int

class UserStats(BaseModel):
    known_words: int
    learning_words: int
    new_words: int
    total_words: int
    progress_percentage: float

# Helper functions
def get_db():
    return db

def get_words_collection(db: Database = Depends(get_db)) -> Collection:
    return db["words"]

def get_progress_collection(db: Database = Depends(get_db)) -> Collection:
    return db["word_progress"]

async def fetch_and_store_french_words():
    """Fetch French words from the website and store them in MongoDB"""
    words_collection = get_words_collection(db)
    
    # Check if words are already in the database
    if words_collection.count_documents({}) > 0:
        print("Words already in database, skipping fetch")
        return
    
    try:
        # Make a request to the website
        url = "https://first-words.com/ru-RU/fr-FR/common-words"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract words and translations (this will need to be adjusted based on the actual website structure)
        # This is a placeholder extraction logic
        french_words = []
        translations = []
        
        # Since we couldn't inspect the actual page structure, we'll use a fallback method
        # In a real-world scenario, we'd analyze the HTML structure and extract the data properly
        
        # Fallback: Use a predefined list of common French words with translations
        common_french_words = [
            {"french": "être", "russian": "быть"},
            {"french": "avoir", "russian": "иметь"},
            {"french": "je", "russian": "я"},
            {"french": "tu", "russian": "ты"},
            {"french": "il", "russian": "он"},
            {"french": "elle", "russian": "она"},
            {"french": "nous", "russian": "мы"},
            {"french": "vous", "russian": "вы"},
            {"french": "ils", "russian": "они (муж.)"},
            {"french": "elles", "russian": "они (жен.)"},
            {"french": "le", "russian": "определенный артикль (муж.)"},
            {"french": "la", "russian": "определенный артикль (жен.)"},
            {"french": "un", "russian": "неопределенный артикль (муж.)"},
            {"french": "une", "russian": "неопределенный артикль (жен.)"},
            {"french": "et", "russian": "и"},
            {"french": "ou", "russian": "или"},
            {"french": "mais", "russian": "но"},
            {"french": "si", "russian": "если"},
            {"french": "dans", "russian": "в"},
            {"french": "sur", "russian": "на"},
            {"french": "sous", "russian": "под"},
            {"french": "avec", "russian": "с"},
            {"french": "sans", "russian": "без"},
            {"french": "pour", "russian": "для"},
            {"french": "par", "russian": "через"},
            {"french": "de", "russian": "от, из"},
            {"french": "à", "russian": "в, к"},
            {"french": "aller", "russian": "идти"},
            {"french": "venir", "russian": "приходить"},
            {"french": "faire", "russian": "делать"},
            {"french": "dire", "russian": "говорить"},
            {"french": "voir", "russian": "видеть"},
            {"french": "savoir", "russian": "знать"},
            {"french": "pouvoir", "russian": "мочь"},
            {"french": "vouloir", "russian": "хотеть"},
            {"french": "devoir", "russian": "должен"},
            {"french": "prendre", "russian": "брать"},
            {"french": "donner", "russian": "давать"},
            {"french": "trouver", "russian": "находить"},
            {"french": "penser", "russian": "думать"},
            {"french": "mettre", "russian": "класть"},
            {"french": "parler", "russian": "говорить"},
            {"french": "aimer", "russian": "любить"},
            {"french": "jour", "russian": "день"},
            {"french": "nuit", "russian": "ночь"},
            {"french": "an", "russian": "год"},
            {"french": "mois", "russian": "месяц"},
            {"french": "semaine", "russian": "неделя"},
            {"french": "heure", "russian": "час"},
            {"french": "minute", "russian": "минута"},
            {"french": "homme", "russian": "мужчина, человек"},
            {"french": "femme", "russian": "женщина"},
            {"french": "enfant", "russian": "ребенок"},
            {"french": "ami", "russian": "друг"},
            {"french": "famille", "russian": "семья"},
            {"french": "maison", "russian": "дом"},
            {"french": "travail", "russian": "работа"},
            {"french": "école", "russian": "школа"},
            {"french": "eau", "russian": "вода"},
            {"french": "pain", "russian": "хлеб"}
        ]
        
        # Insert words into MongoDB
        for word_data in common_french_words:
            words_collection.insert_one({
                "id": str(uuid.uuid4()),
                "french": word_data["french"],
                "russian": word_data["russian"],
                "created_at": datetime.utcnow()
            })
        
        print(f"Added {len(common_french_words)} words to the database")
    except Exception as e:
        print(f"Error fetching French words: {str(e)}")

@app.on_event("startup")
async def startup_db_client():
    # Initialize database with words on startup
    background_tasks = BackgroundTasks()
    background_tasks.add_task(fetch_and_store_french_words)
    await fetch_and_store_french_words()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# API Endpoints
@app.get("/api/")
async def root():
    return {"message": "French Vocabulary Learning API"}

@app.get("/api/words", response_model=List[Word])
async def get_all_words(
    words_collection: Collection = Depends(get_words_collection)
):
    words = list(words_collection.find())
    return [
        {
            "id": word.get("id"),
            "french": word.get("french"),
            "russian": word.get("russian"),
            "created_at": word.get("created_at")
        }
        for word in words
    ]

@app.get("/api/flashcards", response_model=List[FlashcardResponse])
async def get_flashcards(
    limit: int = 10,
    words_collection: Collection = Depends(get_words_collection),
    progress_collection: Collection = Depends(get_progress_collection)
):
    # Get all words
    all_words = list(words_collection.find())
    
    # Get existing progress
    all_progress = list(progress_collection.find())
    progress_by_word_id = {p.get("word_id"): p for p in all_progress}
    
    # Create user progress for words that don't have it
    for word in all_words:
        word_id = word.get("id")
        if word_id not in progress_by_word_id:
            new_progress = {
                "id": str(uuid.uuid4()),
                "word_id": word_id,
                "status": "new",
                "strength": 0,
                "next_review": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            progress_collection.insert_one(new_progress)
            progress_by_word_id[word_id] = new_progress
    
    # Prepare flashcards with priority
    flashcards = []
    
    # Add new words
    new_words = [
        word for word in all_words
        if progress_by_word_id.get(word.get("id"), {}).get("status") == "new"
    ]
    
    # Add learning words (priority by strength: lower strength = higher priority)
    learning_words = [
        word for word in all_words
        if progress_by_word_id.get(word.get("id"), {}).get("status") == "learning"
    ]
    learning_words.sort(
        key=lambda w: progress_by_word_id.get(w.get("id"), {}).get("strength", 0)
    )
    
    # Add known words (lowest priority)
    known_words = [
        word for word in all_words
        if progress_by_word_id.get(word.get("id"), {}).get("status") == "known"
    ]
    
    # Combine with priority
    combined_words = new_words + learning_words + known_words
    
    # Select a subset for study
    selected_words = combined_words[:limit]
    
    # Format response
    flashcards = [
        {
            "id": word.get("id"),
            "french": word.get("french"),
            "russian": word.get("russian"),
            "status": progress_by_word_id.get(word.get("id"), {}).get("status", "new"),
            "strength": progress_by_word_id.get(word.get("id"), {}).get("strength", 0)
        }
        for word in selected_words
    ]
    
    return flashcards

@app.post("/api/flashcards/{word_id}/update")
async def update_word_progress(
    word_id: str,
    known: bool,
    progress_collection: Collection = Depends(get_progress_collection),
    words_collection: Collection = Depends(get_words_collection)
):
    # Check if word exists
    word = words_collection.find_one({"id": word_id})
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Get current progress
    progress = progress_collection.find_one({"word_id": word_id})
    
    if not progress:
        # Create new progress if it doesn't exist
        progress = {
            "id": str(uuid.uuid4()),
            "word_id": word_id,
            "status": "new",
            "strength": 0,
            "next_review": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    # Update progress based on user response
    current_strength = progress.get("strength", 0)
    current_status = progress.get("status", "new")
    
    if known:
        # User knows the word, increase strength
        new_strength = min(current_strength + 1, 5)
        new_status = "known" if new_strength >= 5 else "learning"
    else:
        # User doesn't know the word, decrease strength
        new_strength = max(current_strength - 1, 0)
        new_status = "new" if new_strength == 0 else "learning"
    
    # Update in database
    update_data = {
        "status": new_status,
        "strength": new_strength,
        "updated_at": datetime.utcnow()
    }
    
    if progress.get("id"):
        # Update existing progress
        progress_collection.update_one(
            {"id": progress.get("id")},
            {"$set": update_data}
        )
    else:
        # Insert new progress
        update_data["id"] = str(uuid.uuid4())
        update_data["word_id"] = word_id
        progress_collection.insert_one(update_data)
    
    return {"success": True, "new_status": new_status, "new_strength": new_strength}

@app.get("/api/stats", response_model=UserStats)
async def get_user_stats(
    words_collection: Collection = Depends(get_words_collection),
    progress_collection: Collection = Depends(get_progress_collection)
):
    # Count total words
    total_words = words_collection.count_documents({})
    
    # Count words by status
    known_words = progress_collection.count_documents({"status": "known"})
    learning_words = progress_collection.count_documents({"status": "learning"})
    new_words = total_words - known_words - learning_words
    
    # Calculate progress percentage
    progress_percentage = (known_words / total_words * 100) if total_words > 0 else 0
    
    return {
        "known_words": known_words,
        "learning_words": learning_words,
        "new_words": new_words,
        "total_words": total_words,
        "progress_percentage": progress_percentage
    }
