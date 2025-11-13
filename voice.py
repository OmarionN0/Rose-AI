#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# voice.py - Voice Handler for Project ROSE
#
# Handles text-to-speech and speech recognition using Bluetooth microphone

import pyttsx3
import speech_recognition as sr
import subprocess
import re


class VoiceHandler:
    def __init__(self, prefer_bluetooth=True):
        """
        Initialize the text-to-speech engine and speech recognizer.
        
        Args:
            prefer_bluetooth: If True, automatically selects Bluetooth mic if found
        """
        # Initialize TTS engine
        self.engine = pyttsx3.init(driverName='espeak')
        
        # Optional: Customize voice properties
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Configure recognizer for better performance
        self.recognizer.energy_threshold = 300  # Lower = more sensitive
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # Seconds of silence before phrase ends
        
        # Detect and select microphone
        self._select_microphone(prefer_bluetooth)
        
        # Try to set Bluetooth to headset mode if using Bluetooth
        if self.mic_index is not None and prefer_bluetooth:
            self._set_bluetooth_headset_mode()
    
    def _select_microphone(self, prefer_bluetooth):
        """Detect available microphones and select the best one."""
        print("\n" + "=" * 50)
        print("AVAILABLE MICROPHONES:")
        print("=" * 50)
        
        self.mic_names = sr.Microphone.list_microphone_names()
        
        if not self.mic_names:
            print("No microphones detected!")
            self.mic_index = None
            return
        
        for i, name in enumerate(self.mic_names):
            print(f"  [{i}] {name}")
        
        # Try to find Bluetooth mic
        self.mic_index = None
        
        if prefer_bluetooth:
            bluetooth_keywords = ["bluez", "crusher", "bluetooth", "bt", "wireless"]
            for i, name in enumerate(self.mic_names):
                if any(keyword in name.lower() for keyword in bluetooth_keywords):
                    self.mic_index = i
                    print(f"\nAuto-selected Bluetooth mic: {name}")
                    break
        
        # Fallback to default mic
        if self.mic_index is None:
            self.mic_index = None  # Use system default instead of device 0
            print(f"\nUsing system default microphone")
        
        print("=" * 50 + "\n")
    
    def _set_bluetooth_headset_mode(self):
        """Attempt to switch Bluetooth device to HSP/HFP (headset) mode."""
        try:
            # Get list of PulseAudio cards
            result = subprocess.run(
                ['pactl', 'list', 'cards', 'short'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Find bluez card
            for line in result.stdout.split('\n'):
                if 'bluez_card' in line:
                    card_name = line.split()[1]
                    print(f"Found Bluetooth card: {card_name}")
                    
                    # Try to set to headset mode
                    subprocess.run(
                        ['pactl', 'set-card-profile', card_name, 'headset_head_unit'],
                        capture_output=True,
                        timeout=5
                    )
                    print("Switched to Headset (HSP/HFP) mode for microphone")
                    return
                    
        except FileNotFoundError:
            print("PulseAudio (pactl) not found - install with: sudo apt-get install pulseaudio-utils")
        except subprocess.TimeoutExpired:
            print("Timeout switching Bluetooth profile")
        except Exception as e:
            print(f"Could not auto-switch Bluetooth mode: {e}")
            print("    Try manually: pavucontrol → Configuration → Select 'Headset Head Unit'")
    
    def speak(self, text):
        """
        Make ROSE speak the given text.
        
        Args:
            text: String to speak
        """
        print(f"ROSE: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """
        Listen through microphone and convert speech to text.
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for a phrase
            
        Returns:
            String of recognized text (lowercase) or empty string
        """
        try:
            # Use system default if mic_index is None, otherwise use specific device
            mic_params = {
                "sample_rate": 16000,
                "chunk_size": 2048
            }
            if self.mic_index is not None:
                mic_params["device_index"] = self.mic_index
            
            print(f"Opening microphone...")
            with sr.Microphone(**mic_params) as source:
                print("Mic opened. Listening...", end=" ", flush=True)
                
                # Adjust for ambient noise with more time
                print("Calibrating...", end=" ", flush=True)
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                print("Processing...")
                
                # Recognize speech using Google's API
                text = self.recognizer.recognize_google(audio)
                print(f"You: {text}")
                return text.lower()
                
        except sr.WaitTimeoutError:
            print("Timeout - no speech detected")
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error: {e}")
            return ""
    
    def set_voice_properties(self, rate=None, volume=None):
        """
        Adjust voice properties.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        if rate is not None:
            self.engine.setProperty('rate', rate)
        if volume is not None:
            self.engine.setProperty('volume', volume)


# Test the voice handler if run directly
if __name__ == "__main__":
    print("\nTesting Voice Handler...\n")
    
    rose = VoiceHandler()
    rose.speak("Hello, I am Rose. Voice handler test initiated.")
    
    rose.speak("Please say something to test the microphone.")
    command = rose.listen()
    
    if command:
        rose.speak(f"You said: {command}")
        rose.speak("Voice handler test complete.")
    else:
        rose.speak("No input detected. Please check your microphone.")
