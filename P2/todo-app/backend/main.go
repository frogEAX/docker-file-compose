package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	_ "github.com/lib/pq"
)

type Todo struct {
	ID   int    `json:"id"`
	Text string `json:"text"`
	Done bool   `json:"done"`
}

var db *sql.DB

func main() {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		dsn = "postgres://postgres:postgres@localhost:5432/todos?sslmode=disable"
	}

	var err error
	db, err = sql.Open("postgres", dsn)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	if err = db.Ping(); err != nil {
		log.Fatal("cannot connect to db:", err)
	}

	http.HandleFunc("/todos", cors(todosHandler))
	http.HandleFunc("/todos/", cors(todoHandler))

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Println("listening on :" + port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func cors(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next(w, r)
	}
}

func todosHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	switch r.Method {
	case http.MethodGet:
		rows, err := db.Query("SELECT id, text, done FROM todos ORDER BY id")
		if err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		defer rows.Close()
		todos := []Todo{}
		for rows.Next() {
			var t Todo
			rows.Scan(&t.ID, &t.Text, &t.Done)
			todos = append(todos, t)
		}
		json.NewEncoder(w).Encode(todos)

	case http.MethodPost:
		var t Todo
		json.NewDecoder(r.Body).Decode(&t)
		err := db.QueryRow("INSERT INTO todos(text, done) VALUES($1, false) RETURNING id", t.Text).Scan(&t.ID)
		if err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(t)
	}
}

func todoHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	idStr := strings.TrimPrefix(r.URL.Path, "/todos/")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "bad id", 400)
		return
	}

	switch r.Method {
	case http.MethodPut:
		var t Todo
		json.NewDecoder(r.Body).Decode(&t)
		db.Exec("UPDATE todos SET done=$1 WHERE id=$2", t.Done, id)
		w.WriteHeader(http.StatusNoContent)

	case http.MethodDelete:
		db.Exec("DELETE FROM todos WHERE id=$1", id)
		w.WriteHeader(http.StatusNoContent)
	}
}
