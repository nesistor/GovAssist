package data

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"log"
	"time"
)

const dbTimeout = time.Second * 3

type ChatSessionModel struct {
	DB *sql.DB
}

type ChatSession struct {
	ID           int64     `json:"id"`
	UserID       int64     `json:"user_id"`
	SessionName  string    `json:"session_name"`
	Conversation []Message `json:"conversation"` // Typ Message reprezentuje pojedyncze wiadomości
	CreatedAt    time.Time `json:"created_at"`
}

type Message struct {
	Sender    string `json:"sender"` // 'user' lub 'assistant'
	Content   string `json:"content"`
	Timestamp string `json:"timestamp"`
}

// CreateSession dodaje nową sesję do bazy danych
func (c *ChatSessionModel) CreateSession(session ChatSession) (int64, error) {
	ctx, cancel := context.WithTimeout(context.Background(), dbTimeout)
	defer cancel()

	// Konwersja rozmowy do formatu JSON
	conversationJSON, err := json.Marshal(session.Conversation)
	if err != nil {
		return 0, err
	}

	query := `INSERT INTO chat_sessions (user_id, session_name, conversation, created_at)
	          VALUES ($1, $2, $3, $4) RETURNING id`

	var newID int64
	err = c.DB.QueryRowContext(ctx, query,
		session.UserID,
		session.SessionName,
		conversationJSON,
		time.Now(),
	).Scan(&newID)

	if err != nil {
		return 0, err
	}

	return newID, nil
}

// GetSessionByID pobiera jedną sesję na podstawie jej ID
func (c *ChatSessionModel) GetSessionByID(id int64) (*ChatSession, error) {
	ctx, cancel := context.WithTimeout(context.Background(), dbTimeout)
	defer cancel()

	query := `SELECT id, user_id, session_name, conversation, created_at FROM chat_sessions WHERE id = $1`

	var session ChatSession
	var conversationJSON []byte

	err := c.DB.QueryRowContext(ctx, query, id).Scan(
		&session.ID,
		&session.UserID,
		&session.SessionName,
		&conversationJSON,
		&session.CreatedAt,
	)

	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, nil // brak wyników
		}
		return nil, err
	}

	// Dekodowanie rozmowy z JSON
	err = json.Unmarshal(conversationJSON, &session.Conversation)
	if err != nil {
		return nil, err
	}

	return &session, nil
}

// GetAllSessionsByUserID zwraca wszystkie sesje dla danego użytkownika
func (c *ChatSessionModel) GetAllSessionsByUserID(userID int64) ([]ChatSession, error) {
	ctx, cancel := context.WithTimeout(context.Background(), dbTimeout)
	defer cancel()

	query := `SELECT id, user_id, session_name, conversation, created_at FROM chat_sessions WHERE user_id = $1 ORDER BY created_at DESC`

	rows, err := c.DB.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sessions []ChatSession

	for rows.Next() {
		var session ChatSession
		var conversationJSON []byte

		err := rows.Scan(
			&session.ID,
			&session.UserID,
			&session.SessionName,
			&conversationJSON,
			&session.CreatedAt,
		)
		if err != nil {
			log.Println("Error scanning", err)
			return nil, err
		}

		// Dekodowanie rozmowy z JSON
		err = json.Unmarshal(conversationJSON, &session.Conversation)
		if err != nil {
			log.Println("Error unmarshalling conversation", err)
			return nil, err
		}

		sessions = append(sessions, session)
	}

	return sessions, nil
}

// UpdateSessionConversation aktualizuje rozmowę w istniejącej sesji
func (c *ChatSessionModel) UpdateSessionConversation(sessionID int64, newMessages []Message) error {
	ctx, cancel := context.WithTimeout(context.Background(), dbTimeout)
	defer cancel()

	// Pobierz istniejącą sesję
	session, err := c.GetSessionByID(sessionID)
	if err != nil {
		return err
	}
	if session == nil {
		return errors.New("session not found")
	}

	// Dodaj nowe wiadomości do istniejącej rozmowy
	session.Conversation = append(session.Conversation, newMessages...)

	// Konwersja rozmowy do JSON
	conversationJSON, err := json.Marshal(session.Conversation)
	if err != nil {
		return err
	}

	query := `UPDATE chat_sessions SET conversation = $1 WHERE id = $2`

	_, err = c.DB.ExecContext(ctx, query, conversationJSON, sessionID)
	if err != nil {
		return err
	}

	return nil
}

// DeleteSession usuwa sesję z bazy danych
func (c *ChatSessionModel) DeleteSession(sessionID int64) error {
	ctx, cancel := context.WithTimeout(context.Background(), dbTimeout)
	defer cancel()

	query := `DELETE FROM chat_sessions WHERE id = $1`

	_, err := c.DB.ExecContext(ctx, query, sessionID)
	if err != nil {
		return err
	}

	return nil
}
