package main

import (
	"fmt"
	"net/http"
	"strconv"
	"time"

	"chatsession-service/data"
)

// GetAllChatSessions retrieves all chat sessions.
func (app *Config) GetAllChatSessions(w http.ResponseWriter, r *http.Request) {
	sessions, err := app.Models.ChatSession.GetAllChatSessions()
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

	session, err := app.Models.ChatSession.GetChatSessionByID(sessionID)
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
		StartedAt   string `json:"started_at"`
		Description string `json:"description"`
	}

	err := app.readJSON(w, r, &requestPayload)
	if err != nil {
		app.errorJSON(w, err, http.StatusBadRequest)
		return
	}

	startedAt, err := time.Parse(time.RFC3339, requestPayload.StartedAt)
	if err != nil {
		app.errorJSON(w, fmt.Errorf("invalid date format for started_at"), http.StatusBadRequest)
		return
	}

	session := data.ChatSession{
		UserID:      requestPayload.UserID,
		StartedAt:   startedAt,
		Description: requestPayload.Description,
	}

	sessionID, err := app.Models.ChatSession.InsertChatSession(session)
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

// UpdateChatSession updates an existing chat session.
func (app *Config) UpdateChatSession(w http.ResponseWriter, r *http.Request) {
	idStr := r.URL.Query().Get("id")
	sessionID, err := strconv.Atoi(idStr)
	if err != nil {
		app.errorJSON(w, fmt.Errorf("invalid session ID"), http.StatusBadRequest)
		return
	}

	var requestPayload struct {
		Description string `json:"description"`
	}

	err = app.readJSON(w, r, &requestPayload)
	if err != nil {
		app.errorJSON(w, err, http.StatusBadRequest)
		return
	}

	session := data.ChatSession{
		ID:          sessionID,
		Description: requestPayload.Description,
		UpdatedAt:   time.Now(),
	}

	err = app.Models.ChatSession.UpdateChatSession(session)
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

	err = app.Models.ChatSession.DeleteChatSession(sessionID)
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
