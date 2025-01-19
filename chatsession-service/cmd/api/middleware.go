package main

import (
	"context"
	"fmt"
	"net/http"
	"strings"

	"firebase.google.com/go/v4/auth"
)

// FirebaseAuthMiddleware sprawdza i weryfikuje token Firebase
func (app *Config) FirebaseAuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Pobierz nagłówek Authorization
		authHeader := r.Header.Get("Authorization")

		if authHeader == "" {
			app.errorJSON(w, fmt.Errorf("missing authorization header"), http.StatusUnauthorized)
			return
		}

		// Wyciągnij token (zakładamy schemat "Bearer <TOKEN>")
		tokenString := strings.TrimPrefix(authHeader, "Bearer ")

		if tokenString == authHeader {
			app.errorJSON(w, fmt.Errorf("invalid authorization header format"), http.StatusUnauthorized)
			return
		}

		// Zweryfikuj token za pomocą Firebase Admin SDK
		token, err := app.FirebaseAuthClient.VerifyIDToken(context.Background(), tokenString)
		if err != nil {
			app.errorJSON(w, fmt.Errorf("invalid or expired token: %v", err), http.StatusUnauthorized)
			return
		}

		// Dodaj dane użytkownika do kontekstu
		ctx := context.WithValue(r.Context(), "user", token)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// GetUserFromContext wyciąga dane użytkownika z kontekstu
func GetUserFromContext(ctx context.Context) (*auth.Token, error) {
	user, ok := ctx.Value("user").(*auth.Token)
	if !ok {
		return nil, fmt.Errorf("user not found in context")
	}
	return user, nil
}
