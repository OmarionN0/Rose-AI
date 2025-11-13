#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# main.py - Project ROSE Main Loop
#
# Copyright 2025 Bob@raspberrypi5
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys
from datetime import datetime
from voice import VoiceHandler
from ollama import OllamaHandler  # FIXED: correct import


def main():
    """Main loop for Project ROSE voice assistant."""
    
    # Startup banner
    print("\n" + "=" * 50)
    print("    PROJECT R.O.S.E. - Voice Assistant")
    print("    Raspberry Operated Speech Engine")
    print("=" * 50 + "\n")
    
    try:
        # Initialize the voice system
        rose = VoiceHandler(prefer_bluetooth=True)
        
        # Initialize AI system with lightweight model to avoid crashes
        # CRITICAL: Use qwen2.5:0.5b (397MB) not phi3:mini (3.8GB)
        ai = OllamaHandler(model="qwen2.5:0.5b")
        
        # Startup greeting
        rose.speak("System online. Rose activated and ready.")
        if ai.is_available():
            rose.speak("Artificial intelligence module loaded. I can help with cybersecurity questions.")
        else:
            rose.speak("Running in basic mode. AI features unavailable.")
        rose.speak("Say hey rose to get my attention, or say exit to shut down.")
        
        # Main interaction loop
        while True:
            try:
                # Listen for user input (with longer timeout for Bluetooth)
                command = rose.listen(timeout=10)
                
                # Skip empty commands
                if not command:
                    continue
                
                # Process commands
                if "hey rose" in command or "hello rose" in command:
                    rose.speak("Yes? How can I help you?")
                
                elif "hello" in command or "hi" in command:
                    rose.speak("Hello! I'm here and listening.")
                
                elif "what time" in command or "tell me the time" in command:
                    now = datetime.now()
                    time_str = now.strftime("%I:%M %p")
                    rose.speak(f"The time is {time_str}.")
                
                elif "what day" in command or "what's the date" in command:
                    now = datetime.now()
                    date_str = now.strftime("%A, %B %d, %Y")
                    rose.speak(f"Today is {date_str}.")
                
                elif "how are you" in command:
                    rose.speak("I'm functioning optimally. All systems nominal.")
                
                elif "thank you" in command or "thanks" in command:
                    rose.speak("You're welcome!")
                
                elif "clear history" in command or "reset conversation" in command:
                    if ai.is_available():
                        ai.clear_history()
                        rose.speak("Conversation history cleared.")
                    else:
                        rose.speak("AI is not available.")
                
                elif "check for updates" in command or "check updates" in command:
                    rose.speak("Checking for updates...")
                    has_updates, version = updater.check_for_updates()
                    if has_updates:
                        rose.speak(f"Updates available. Version {version}. Say update rose to install.")
                    else:
                        rose.speak("You're running the latest version.")
                
                elif "update rose" in command or "update yourself" in command:
                    rose.speak("Starting update process. Creating backup...")
                    success = updater.perform_update()
                    if success:
                        rose.speak("Update complete! I need to restart. Shutting down now.")
                        break
                    else:
                        rose.speak("Update failed. I'm still running the old version.")
                
                elif "what version" in command or "your version" in command:
                    version = updater.get_current_version()
                    rose.speak(f"I'm running version {version}.")
                
                elif "exit" in command or "goodbye" in command or "shut down" in command:
                    rose.speak("Understood. Rose shutting down. Goodbye.")
                    break
                
                else:
                    # Use AI for everything else
                    if ai.is_available():
                        rose.speak("Thinking...")
                        response = ai.ask(command)
                        rose.speak(response)
                    else:
                        # Echo back unrecognized commands
                        rose.speak(f"I heard: {command}. I'm still learning new commands.")
                    
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\n\n⚠️  Keyboard interrupt detected")
                rose.speak("Manual interrupt received. Going offline.")
                break
            
            except Exception as e:
                # Handle unexpected errors
                print(f"\n❌ Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                rose.speak("An error occurred. Please check the console.")
                # Don't break - try to recover
    
    except Exception as e:
        # Handle initialization errors
        print(f"\n❌ Fatal error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Clean exit
    print("\n" + "=" * 50)
    print("    PROJECT ROSE TERMINATED")
    print("=" * 50 + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
