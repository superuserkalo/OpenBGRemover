# go-api/Dockerfile

# --- Stage 1: The Builder ---
# Use a lightweight Alpine-based Go image to build our application
FROM golang:1.22-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the Go module files and download dependencies first for caching
COPY go.mod go.sum* ./
RUN go mod download

# Copy the rest of the application source code
COPY . .

# Build the application into a static binary. This is for the single-file setup.
RUN CGO_ENABLED=0 go build -o /app/server .

# --- Stage 2: The Final Image ---
# Use a completely empty 'scratch' image for a tiny and secure final container
FROM scratch

# Set the working directory
WORKDIR /app

# Copy ONLY the compiled binary from the 'builder' stage
COPY --from=builder /app/server .

# Expose the port the Go server will run on
EXPOSE 8080

# The command to run when the container starts
CMD ["/app/server"]
