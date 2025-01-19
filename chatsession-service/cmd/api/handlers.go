package main

import (
	"fmt"
	"net/http"
	"strconv"

	"chatsession-service/data"
)

// GetAllChatSessions retrieves all chat sessions for a specific user.
func (app *Config) GetAllChatSessions(w http.ResponseWriter, r *http.Request) {
	userIDStr := r.URL.Query().Get("user_id") // Assuming you are passing user_id as a query param
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		app.errorJSON(w, fmt.Errorf("invalid user ID"), http.StatusBadRequest)
		return
	}

	// Corrected method call: GetAllSessionsByUserID
	sessions, err := app.Models.GetAllSessionsByUserID(int64(userID))
	if err != nil {
		app.errorJSON(w, err, http.StatusInternalServerError)
		return
	}

	payload := jsonResponse{
		Error:   false,
		Message: "Chat sessions retrieved successfully",
		Data:    sessions,
	}

	app.writeJSON(w, http.StatusOK, payload)
}

// GetChatSessionByID retrieves a single chat session by its ID.
func (app *Config) GetChatSessionByID(w http.ResponseWriter, r *http.Request) {
	idStr := r.URL.Query().Get("id")
	sessionID, err := strconv.Atoi(idStr)
	if err != nil {
		app.errorJSON(w, fmt.Errorf("invalid session ID"), http.StatusBadRequest)
		return
	}

	// Corrected method call: GetSessionByID
	session, err := app.Models.GetSessionByID(int64(sessionID))
	if err != nil {
		app.errorJSON(w, err, http.StatusNotFound)
		return
	}

	payload := jsonResponse{
		Error:   false,
		Message: "Chat session retrieved successfully",
		Data:    session,
	}

	app.writeJSON(w, http.StatusOK, payload)
}

// CreateChatSession creates a new chat session.
func (app *Config) CreateChatSession(w http.ResponseWriter, r *http.Request) {
	var requestPayload struct {
		UserID      int    `json:"user_id"`
		SessionName string `json:"session_name"`
	}

	err := app.readJSON(w, r, &requestPayload)
	if err != nil {
		app.errorJSON(w, err, http.StatusBadRequest)
		return
	}

	// Convert int to int64 for UserID
	session := data.ChatSession{
		UserID:      int64(requestPayload.UserID), // Corrected type
		SessionName: requestPayload.SessionName,
	}

	// Corrected method call: CreateSession
	sessionID, err := app.Models.CreateSession(session)
	if err != nil {
		app.errorJSON(w, err, http.StatusInternalServerError)
		return
	}

	payload := jsonResponse{
		Error:   false,
		Message: "Chat session created successfully",
		Data: map[string]interface{}{
			"session_id": sessionID,
		},
	}

	app.writeJSON(w, http.StatusCreated, payload)
}

// UpdateChatSession updates an existing chat session with new messages.
func (app *Config) UpdateChatSession(w http.ResponseWriter, r *http.Request) {
	idStr := r.URL.Query().Get("id")
	sessionID, err := strconv.Atoi(idStr)
	if err != nil {
		app.errorJSON(w, fmt.Errorf("invalid session ID"), http.StatusBadRequest)
		return
	}

	var requestPayload struct {
		Messages []data.Message `json:"messages"`
	}

	err = app.readJSON(w, r, &requestPayload)
	if err != nil {
		app.errorJSON(w, err, http.StatusBadRequest)
		return
	}

	// Corrected method call: UpdateSessionConversation
	err = app.Models.UpdateSessionConversation(int64(sessionID), requestPayload.Messages)
	if err != nil {
		app.errorJSON(w, err, http.StatusInternalServerError)
		return
	}

	payload := jsonResponse{
		Error:   false,
		Message: "Chat session updated successfully",
	}

	app.writeJSON(w, http.StatusOK, payload)
}

// DeleteChatSession deletes a chat session by its ID.
func (app *Config) DeleteChatSession(w http.ResponseWriter, r *http.Request) {
	idStr := r.URL.Query().Get("id")
	sessionID, err := strconv.Atoi(idStr)
	if err != nil {
		app.errorJSON(w, fmt.Errorf("invalid session ID"), http.StatusBadRequest)
		return
	}

	// Corrected method call: DeleteSession
	err = app.Models.DeleteSession(int64(sessionID))
	if err != nil {
		app.errorJSON(w, err, http.StatusInternalServerError)
		return
	}

	payload := jsonResponse{
		Error:   false,
		Message: fmt.Sprintf("Chat session with ID %d deleted successfully", sessionID),
	}

	app.writeJSON(w, http.StatusOK, payload)
}
