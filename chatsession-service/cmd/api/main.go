package main

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"chatsession-service/data"

	"firebase.google.com/go/v4"
	"firebase.google.com/go/v4/auth"
	"google.golang.org/api/option"

	_ "github.com/jackc/pgconn"
	_ "github.com/jackc/pgx/v4"
	_ "github.com/jackc/pgx/v4/stdlib"
)

const (
	webPort = "80"
)

var counts int64

// Config holds the application configuration
type Config struct {
	DB               *sql.DB
	Models           data.ChatSessionModel
	FirebaseAuthClient *auth.Client // Dodajemy pole do przechowywania klienta Firebase Auth
}

func main() {
	log.Println("Starting chat service")

	// Connect to the database
	conn := connectToDB()
	if conn == nil {
		log.Panic("Can't connect to Postgres!")
	}

	// Set up Firebase Auth client
	firebaseAuthClient, err := setupFirebaseAuth()
	if err != nil {
		log.Panic("Error setting up Firebase Auth: ", err)
	}

	// Set up the application configuration
	app := Config{
		DB:               conn,
		Models:           data.ChatSessionModel{DB: conn},
		FirebaseAuthClient: firebaseAuthClient, // Przypisanie klienta Firebase Auth
	}

	// Start the HTTP server
	srv := &http.Server{
		Addr:    fmt.Sprintf(":%s", webPort),
		Handler: app.routes(),
	}

	log.Printf("Starting server on port %s", webPort)

	err = srv.ListenAndServe()
	if err != nil {
		log.Panic(err)
	}
}

// setupFirebaseAuth ustawia klienta Firebase Auth
func setupFirebaseAuth() (*auth.Client, error) {
	// Ścieżka do pliku z kluczem Firebase Admin SDK
	// Można ją ustawić jako zmienną środowiskową lub twardo wpisać w kodzie.
	serviceAccount := os.Getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
	if serviceAccount == "" {
		return nil, fmt.Errorf("missing FIREBASE_SERVICE_ACCOUNT_KEY environment variable")
	}

	// Inicjalizacja Firebase SDK
	opt := option.WithCredentialsFile(serviceAccount)
	app, err := firebase.NewApp(context.Background(), nil, opt)
	if err != nil {
		return nil, fmt.Errorf("error initializing Firebase app: %v", err)
	}

	// Pobieranie klienta autoryzacji Firebase
	client, err := app.Auth(context.Background())
	if err != nil {
		return nil, fmt.Errorf("error getting Firebase Auth client: %v", err)
	}

	return client, nil
}

func openDB(dsn string) (*sql.DB, error) {
	log.Println("Trying to connect to the database...")

	db, err := sql.Open("pgx", dsn)
	if err != nil {
		return nil, fmt.Errorf("error opening database: %w", err)
	}

	err = db.Ping()
	if err != nil {
		return nil, fmt.Errorf("error pinging database: %w", err)
	}

	log.Println("Successfully connected to the database")
	return db, nil
}

func connectToDB() *sql.DB {
	dsn := os.Getenv("DSN")
	log.Println("DSN:", dsn)

	for {
		connection, err := openDB(dsn)
		if err != nil {
			log.Printf("Error connecting to the database: %v", err)
			counts++
		} else {
			log.Println("Connected to Postgres!")
			return connection
		}

		if counts > 10 {
			log.Println("Too many failed attempts to connect to the database")
			return nil
		}

		log.Println("Backing off for two seconds...")
		time.Sleep(2 * time.Second)
		continue
	}
}
