#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ollama.py
#  
#  Copyright 2025  <Bob@raspberrypi5>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ollama_handler.py - Local AI Integration for Project ROSE
#
# Uses Ollama for free, offline AI conversations

import subprocess
import json


class OllamaHandler:
    def __init__(self, model="phi3:mini"):
        """
        Initialize the Ollama AI handler.
        
        Args:
            model: The Ollama model to use (default: llama3.2:3b)
        """
        self.model = model  # MY model name
        self.conversation_history = []  # MY conversation list
        self.max_history = 2  # Keeps the last 6 exchanges
        
        # System prompt for cybersecurity focus
        self.system_prompt = """You are ROSE (Raspberry Operated Speech Engine), a voice-activated cybersecurity assistant.

Keep responses BRIEF (2-3 sentences) since they'll be spoken aloud. Only expand if asked.

You help with:
- Security concepts and vulnerabilities
- Network security and penetration testing
- Linux security and hardening
- Security tools (nmap, wireshark, metasploit)
- Code security review
- CVE explanations

"""
        
        # Check if Ollama is available
        self._check_ollama()
    
    def _check_ollama(self):
        """Check if Ollama is installed and model is available."""
        try:
            # Check if ollama command exists
            result = subprocess.run(
                ['which', 'ollama'],
                capture_output=True,
                timeout=2
            )
            
            if result.returncode != 0:
                print("Ollama not found. Install with:")
                print(" curl -fsSL https://ollama.com/install.sh | sh")
                self.available = False
                return
            
            # Check if model is downloaded
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if self.model not in result.stdout:
                print(f"Model '{self.model}' not found. Download with:")
                print(f" ollama pull {self.model}")
                self.available = False
                return
            
            self.available = True
            print(f"AI: Ollama ready with model '{self.model}'")
            
        except Exception as e:
            print(f"Error checking Ollama: {e}")
            self.available = False
    
    def is_available(self):
        """Check if AI is available."""
        return self.available
    
    def ask(self, user_message, brief=True):
        """
        Send a message to Ollama and get a response.
        
        Args:
            user_message: The user's question/command
            brief: If True, remind the AI to be concise
            
        Returns:
            AI's response as a string, or None if error
        """
        if not self.is_available():
            return "AI is not available. Please install Ollama and download a model."
        
        try:
            # Build the conversation context stores in a list
            messages = []
            
            # Add system prompt
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Add conversation history
            for msg in self.conversation_history:
                messages.append(msg)
            
            # Add current user message
            if brief:
                user_message = f"{user_message}\n\n(Keep response brief - 2-3 sentences for voice output)"
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Create prompt for Ollama
            prompt = self._format_messages(messages)
            
            # Call Ollama
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True,
                timeout=60  # 30 second timeout for response
            )
            
            if result.returncode != 0:
                print(f"Ollama error: {result.stderr}")
                return "I'm having trouble thinking right now. Please try again."
            
            response = result.stdout.strip()
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Keep history manageable using an if statement with the length of the convo
            if len(self.conversation_history) > self.max_history * 2:
                self.conversation_history = self.conversation_history[-self.max_history * 2:]
            
            return response
            
        except subprocess.TimeoutExpired:
            print(" AI thinking timeout")
            return "Sorry, I'm thinking too slowly. Try asking something simpler."
        except Exception as e:
            print(f"AI error: {e}")
            return "Something went wrong with my AI processing."
    
    def _format_messages(self, messages):
        """Format conversation messages into a prompt for Ollama."""
        prompt_parts = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print(" AI: Conversation history cleared")
    
    def set_max_history(self, max_exchanges):
        """Set maximum number of conversation exchanges to remember."""
        self.max_history = max_exchanges


# Test the AI handler if run directly
if __name__ == "__main__":
    print("\nTesting Ollama Handler...\n")
    
    ai = OllamaHandler()
    
    if not ai.is_available():
        print(" Ollama not available. Please install it.")
        exit(1)
    
    print("Ollama is available!\n")
    
    # Test questions
    test_questions = [
        "What is a SQL injection attack?",
        "How can I secure SSH?",
    ]
    
    for question in test_questions:
        print(f"Q: {question}")
        print("Thinking...", end=" ", flush=True)
        response = ai.ask(question)
        print(f"\nA: {response}\n")
        print("-" * 60 + "\n")
