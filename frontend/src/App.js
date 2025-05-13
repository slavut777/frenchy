import { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Flashcard component
const Flashcard = ({ card, onKnow, onDontKnow }) => {
  const [flipped, setFlipped] = useState(false);

  const handleFlip = () => {
    setFlipped(!flipped);
  };
  
  // Audio pronunciation function
  const speakWord = (e) => {
    e.stopPropagation();
    const utterance = new SpeechSynthesisUtterance(card.french);
    utterance.lang = 'fr-FR';
    speechSynthesis.speak(utterance);
  };

  return (
    <div 
      className={`flashcard ${flipped ? 'flipped' : ''}`} 
      onClick={handleFlip}
    >
      <div className="flashcard-inner">
        <div className="flashcard-front">
          <h2>{card.french}</h2>
          <button 
            className="audio-btn" 
            onClick={speakWord}
            title="Прослушать произношение"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
            </svg>
          </button>
          <p className="hint">Нажмите, чтобы увидеть перевод</p>
        </div>
        <div className="flashcard-back">
          <h2>{card.russian}</h2>
          {card.pronunciation && (
            <p className="pronunciation">Произношение: {card.pronunciation}</p>
          )}
          <button 
            className="audio-btn audio-btn-light" 
            onClick={speakWord}
            title="Прослушать произношение"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
            </svg>
          </button>
          <div className="flashcard-actions">
            <button 
              className="btn btn-danger" 
              onClick={(e) => {
                e.stopPropagation();
                setFlipped(false);
                onDontKnow();
              }}
            >
              Не знаю
            </button>
            <button 
              className="btn btn-success" 
              onClick={(e) => {
                e.stopPropagation();
                setFlipped(false);
                onKnow();
              }}
            >
              Знаю
            </button>
          </div>
        </div>
      </div>
      <div className="card-strength">
        <div className="strength-label">Уровень знания:</div>
        <div className="strength-meter">
          {Array.from({ length: 5 }).map((_, index) => (
            <div 
              key={index} 
              className={`strength-dot ${index < card.strength ? 'filled' : ''}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

// Statistics Dashboard component
const StatsDashboard = ({ stats }) => {
  return (
    <div className="stats-dashboard">
      <h2>Your Progress</h2>
      <div className="stats-container">
        <div className="stat-box">
          <h3>Known</h3>
          <div className="stat-value">{stats.known_words}</div>
        </div>
        <div className="stat-box">
          <h3>Learning</h3>
          <div className="stat-value">{stats.learning_words}</div>
        </div>
        <div className="stat-box">
          <h3>Not Started</h3>
          <div className="stat-value">{stats.new_words}</div>
        </div>
        <div className="stat-box">
          <h3>Total</h3>
          <div className="stat-value">{stats.total_words}</div>
        </div>
      </div>
      <div className="progress-container">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${stats.progress_percentage}%` }}
          ></div>
        </div>
        <div className="progress-label">{Math.round(stats.progress_percentage)}% Complete</div>
      </div>
    </div>
  );
};

function App() {
  const [flashcards, setFlashcards] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [stats, setStats] = useState({
    known_words: 0,
    learning_words: 0,
    new_words: 0,
    total_words: 0,
    progress_percentage: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch flashcards
  const fetchFlashcards = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/flashcards`);
      setFlashcards(response.data);
      setCurrentCardIndex(0);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch flashcards:", error);
      setError("Failed to load flashcards. Please try again later.");
      setLoading(false);
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    }
  };

  // Update word progress
  const updateWordProgress = async (wordId, known) => {
    try {
      await axios.post(`${API}/flashcards/${wordId}/update?known=${known}`);
      // After update, fetch new stats
      fetchStats();
    } catch (error) {
      console.error("Failed to update word progress:", error);
    }
  };

  // Handle "I know" button
  const handleKnow = async () => {
    if (flashcards.length === 0) return;
    
    const currentCard = flashcards[currentCardIndex];
    await updateWordProgress(currentCard.id, true);
    
    // Move to next card
    if (currentCardIndex < flashcards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1);
    } else {
      // If we've gone through all cards, fetch new ones
      fetchFlashcards();
    }
  };

  // Handle "I don't know" button
  const handleDontKnow = async () => {
    if (flashcards.length === 0) return;
    
    const currentCard = flashcards[currentCardIndex];
    await updateWordProgress(currentCard.id, false);
    
    // Move to next card
    if (currentCardIndex < flashcards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1);
    } else {
      // If we've gone through all cards, fetch new ones
      fetchFlashcards();
    }
  };

  // Initialize on component mount
  useEffect(() => {
    fetchFlashcards();
    fetchStats();
  }, []);

  return (
    <div className="app-container">
      <header className="header">
        <h1>French Vocabulary Trainer</h1>
        <p>Learn the 1000 most common French words</p>
      </header>
      
      <main className="main-content">
        {loading && <div className="loading">Loading cards...</div>}
        {error && <div className="error">{error}</div>}
        
        {!loading && !error && flashcards.length > 0 && (
          <div className="flashcard-container">
            <Flashcard 
              card={flashcards[currentCardIndex]} 
              onKnow={handleKnow} 
              onDontKnow={handleDontKnow}
            />
            <div className="card-counter">
              Card {currentCardIndex + 1} of {flashcards.length}
            </div>
          </div>
        )}
        
        {!loading && !error && flashcards.length === 0 && (
          <div className="no-cards">
            <p>No flashcards available.</p>
            <button className="btn" onClick={fetchFlashcards}>Refresh</button>
          </div>
        )}
      </main>
      
      <footer className="footer">
        <StatsDashboard stats={stats} />
      </footer>
    </div>
  );
}

export default App;
