package auth

import (
	"crypto/rsa"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"math/big"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// JWKSet represents the JSON Web Key Set from Supabase
type JWKSet struct {
	Keys []JWK `json:"keys"`
}

// JWK represents a single JSON Web Key
type JWK struct {
	Kty string `json:"kty"`
	Use string `json:"use"`
	Kid string `json:"kid"`
	N   string `json:"n"`
	E   string `json:"e"`
}

// SupabaseClaims represents the claims in a Supabase JWT
type SupabaseClaims struct {
	jwt.RegisteredClaims
	Role           string                 `json:"role"`
	Email          string                 `json:"email"`
	UserMetadata   map[string]interface{} `json:"user_metadata"`
	AppMetadata    map[string]interface{} `json:"app_metadata"`
}

// AuthService handles JWT verification and key management
type AuthService struct {
	supabaseURL string
	jwks        *JWKSet
	keys        map[string]*rsa.PublicKey
	lastFetch   time.Time
}

// NewAuthService creates a new auth service
func NewAuthService() (*AuthService, error) {
	supabaseURL := os.Getenv("SUPABASE_URL")
	if supabaseURL == "" {
		return nil, fmt.Errorf("SUPABASE_URL environment variable is required")
	}

	service := &AuthService{
		supabaseURL: supabaseURL,
		keys:        make(map[string]*rsa.PublicKey),
	}

	// Fetch initial JWKS
	if err := service.fetchJWKS(); err != nil {
		return nil, fmt.Errorf("failed to fetch initial JWKS: %w", err)
	}

	return service, nil
}

// fetchJWKS fetches the JSON Web Key Set from Supabase
func (a *AuthService) fetchJWKS() error {
	jwksURL := fmt.Sprintf("%s/.well-known/jwks.json", a.supabaseURL)
	
	resp, err := http.Get(jwksURL)
	if err != nil {
		return fmt.Errorf("failed to fetch JWKS: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("JWKS endpoint returned status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read JWKS response: %w", err)
	}

	var jwks JWKSet
	if err := json.Unmarshal(body, &jwks); err != nil {
		return fmt.Errorf("failed to parse JWKS: %w", err)
	}

	// Convert JWKs to RSA public keys
	keys := make(map[string]*rsa.PublicKey)
	for _, jwk := range jwks.Keys {
		if jwk.Kty == "RSA" && jwk.Use == "sig" {
			pubKey, err := a.jwkToRSAPublicKey(jwk)
			if err != nil {
				continue // Skip invalid keys
			}
			keys[jwk.Kid] = pubKey
		}
	}

	a.jwks = &jwks
	a.keys = keys
	a.lastFetch = time.Now()

	return nil
}

// jwkToRSAPublicKey converts a JWK to an RSA public key
func (a *AuthService) jwkToRSAPublicKey(jwk JWK) (*rsa.PublicKey, error) {
	// Decode the modulus
	nBytes, err := base64.RawURLEncoding.DecodeString(jwk.N)
	if err != nil {
		return nil, fmt.Errorf("failed to decode modulus: %w", err)
	}

	// Decode the exponent
	eBytes, err := base64.RawURLEncoding.DecodeString(jwk.E)
	if err != nil {
		return nil, fmt.Errorf("failed to decode exponent: %w", err)
	}

	// Convert bytes to big integers
	n := new(big.Int).SetBytes(nBytes)
	e := new(big.Int).SetBytes(eBytes)

	// Create RSA public key
	pubKey := &rsa.PublicKey{
		N: n,
		E: int(e.Int64()),
	}

	return pubKey, nil
}

// refreshJWKSIfNeeded refreshes the JWKS if it's been more than 1 hour since last fetch
func (a *AuthService) refreshJWKSIfNeeded() error {
	if time.Since(a.lastFetch) > time.Hour {
		return a.fetchJWKS()
	}
	return nil
}

// VerifyJWT verifies a Supabase JWT token and returns the claims
func (a *AuthService) VerifyJWT(tokenString string) (*SupabaseClaims, error) {
	// Refresh JWKS if needed
	if err := a.refreshJWKSIfNeeded(); err != nil {
		return nil, fmt.Errorf("failed to refresh JWKS: %w", err)
	}

	// Parse the token
	token, err := jwt.ParseWithClaims(tokenString, &SupabaseClaims{}, func(token *jwt.Token) (interface{}, error) {
		// Verify the signing method
		if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}

		// Get the key ID from the token header
		kid, ok := token.Header["kid"].(string)
		if !ok {
			return nil, fmt.Errorf("no kid in token header")
		}

		// Get the public key
		pubKey, exists := a.keys[kid]
		if !exists {
			return nil, fmt.Errorf("public key not found for kid: %s", kid)
		}

		return pubKey, nil
	})

	if err != nil {
		return nil, fmt.Errorf("failed to parse token: %w", err)
	}

	// Verify the token is valid
	if !token.Valid {
		return nil, fmt.Errorf("token is invalid")
	}

	// Extract claims
	claims, ok := token.Claims.(*SupabaseClaims)
	if !ok {
		return nil, fmt.Errorf("failed to extract claims")
	}

	return claims, nil
}

// ExtractTokenFromHeader extracts the JWT token from the Authorization header
func ExtractTokenFromHeader(authHeader string) (string, error) {
	if authHeader == "" {
		return "", fmt.Errorf("authorization header is empty")
	}

	// Check if it's a Bearer token
	if strings.HasPrefix(authHeader, "Bearer ") {
		return strings.TrimPrefix(authHeader, "Bearer "), nil
	}

	// For API keys, return as-is for further processing
	return authHeader, nil
}

// IsAPIKey checks if the token looks like an API key (starts with "bg_")
func IsAPIKey(token string) bool {
	return strings.HasPrefix(token, "bg_")
}

// HashAPIKey creates a hash of an API key for database storage
func HashAPIKey(apiKey string) string {
	// In a real implementation, use a proper hash function like bcrypt or SHA-256
	// For now, we'll use a simple approach (replace with proper hashing)
	return fmt.Sprintf("hashed_%s", apiKey)
}

// GenerateAPIKey generates a new API key with the format bg_live_sk_... or bg_test_sk_...
func GenerateAPIKey(isTest bool) string {
	// Generate a random string (in real implementation, use crypto/rand)
	// This is a simplified version
	prefix := "bg_live_sk_"
	if isTest {
		prefix = "bg_test_sk_"
	}
	
	// Generate random part (replace with proper random generation)
	randomPart := fmt.Sprintf("%d", time.Now().UnixNano())
	return prefix + randomPart
}

// GetKeyPrefix extracts the prefix from an API key for identification
func GetKeyPrefix(apiKey string) string {
	// Return the first 16 characters for identification
	if len(apiKey) > 16 {
		return apiKey[:16]
	}
	return apiKey
}