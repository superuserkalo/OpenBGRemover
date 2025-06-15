package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
)

func debugEnv() {
	fmt.Println("🔍 Environment Debug")
	fmt.Println("==================")

	// 1. Check current working directory
	cwd, err := os.Getwd()
	if err != nil {
		fmt.Printf("❌ Cannot get current directory: %v\n", err)
	} else {
		fmt.Printf("📁 Current directory: %s\n", cwd)
	}

	// 2. Check if .env file exists
	envPath := ".env"
	if _, err := os.Stat(envPath); os.IsNotExist(err) {
		fmt.Printf("❌ .env file does not exist at: %s\n", filepath.Join(cwd, envPath))
	} else {
		fmt.Printf("✅ .env file exists at: %s\n", filepath.Join(cwd, envPath))

		// 3. Read .env file contents
		content, err := os.ReadFile(envPath)
		if err != nil {
			fmt.Printf("❌ Cannot read .env file: %v\n", err)
		} else {
			fmt.Printf("📄 .env file contents:\n%s\n", string(content))
		}
	}

	// 4. Try loading with godotenv
	fmt.Println("🔄 Attempting to load .env with godotenv...")
	err = godotenv.Load()
	if err != nil {
		fmt.Printf("❌ godotenv.Load() failed: %v\n", err)
	} else {
		fmt.Println("✅ godotenv.Load() succeeded")
	}

	// 5. Check environment variables after loading
	fmt.Println("\n🔍 Environment variables after loading:")
	fmt.Printf("BEAM_ENDPOINT_URL: '%s'\n", os.Getenv("BEAM_ENDPOINT_URL"))
	fmt.Printf("BEAM_API_KEY: '%s'\n", os.Getenv("BEAM_API_KEY"))
	fmt.Printf("PORT: '%s'\n", os.Getenv("PORT"))

	// 6. List all environment variables containing "BEAM"
	fmt.Println("\n🔍 All environment variables containing 'BEAM':")
	for _, env := range os.Environ() {
		if len(env) > 4 && (env[:4] == "BEAM" || contains(env, "BEAM")) {
			fmt.Printf("  %s\n", env)
		}
	}
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && s[len(s)-len(substr):] == substr ||
		   len(s) >= len(substr) && s[:len(substr)] == substr ||
		   (len(s) > len(substr) && indexOf(s, substr) >= 0)
}

func indexOf(s, substr string) int {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return i
		}
	}
	return -1
}

func main() {
	debugEnv()
}
