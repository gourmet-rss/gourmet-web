#!/bin/bash

echo "Starting Ollama server..."
ollama serve &  # Start Ollama in the background

sleep 5

echo "Ollama is ready, creating the model..."

ollama pull bge-m3 # Pull embeddings model
