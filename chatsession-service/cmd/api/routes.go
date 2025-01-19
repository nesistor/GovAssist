package main

import (
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
)

func (app *Config) routes() http.Handler {
	mux := chi.NewRouter()

	mux.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"https://*", "http://*"},
		AllowedMethods:   []string{"POST", "PUT", "GET", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Content-Type", "Authorization", "X-CSRF-Token"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: true,
		MaxAge:           300,
	}))

	mux.Use(middleware.Heartbeat("/ping"))


	// Trasy chronione
	mux.Route("/api/chat", func(mux chi.Router) {
		mux.Use(app.FirebaseAuthMiddleware) // Middleware Firebase

		mux.Get("/sessions", app.GetAllChatSessions)
		mux.Get("/session/{id}", app.GetChatSessionByID)
		mux.Post("/session", app.CreateChatSession)
		mux.Put("/session/{id}", app.UpdateChatSession)
		mux.Delete("/session/{id}", app.DeleteChatSession)
	})

	return mux
}
