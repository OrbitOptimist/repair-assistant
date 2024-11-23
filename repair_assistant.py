import cv2
import anthropic
import pyttsx3
import json
import os
import logging
import numpy as np
from time import sleep
from repair_procedure import RepairProcedure

try:
    from config import *
except ImportError:
    from config_example import *

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class RepairAssistant:
    def __init__(self, api_key, docs_path):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', TTS_RATE)
        self.engine.setProperty('volume', TTS_VOLUME)
        self.camera = None
        self.repair_procedure = RepairProcedure(docs_path)
        self.setup_camera()
        
    def setup_camera(self):
        """Initialize and configure the camera or create a demo frame."""
        try:
            self.camera = cv2.VideoCapture(CAMERA_INDEX)
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
                
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, FPS)
        except Exception as e:
            logger.warning(f"Camera not available: {e}. Using demo mode.")
            self.camera = None
            # Create a blank frame for demo mode
            self.demo_frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
            cv2.putText(
                self.demo_frame,
                "Demo Mode - No Camera",
                (50, FRAME_HEIGHT//2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )
            
    def speak(self, text):
        """Convert text to speech and print it."""
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        
    def capture_frame(self):
        """Capture a frame from the camera or return demo frame."""
        if self.camera is not None:
            ret, frame = self.camera.read()
            if not ret:
                raise Exception("Could not capture frame")
        else:
            # Use demo frame
            frame = self.demo_frame.copy()
            
        # Add progress indicator
        progress = self.repair_procedure.get_progress()
        cv2.putText(
            frame,
            f"Progress: {progress}%",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        
        return frame
    
    def get_frame_description(self, frame):
        """Get a description of the current frame for AI analysis."""
        # Convert frame to base64 for API (simplified for demo)
        _, buffer = cv2.imencode('.jpg', frame)
        return "Image shows user attempting repair step"  # Simplified for demo
        
    def get_ai_guidance(self, frame_description, user_input=None):
        """Get AI guidance based on current state and input."""
        current_step = self.repair_procedure.get_current_step()
        tools = self.repair_procedure.get_required_tools()
        
        system_prompt = f"""You are a repair assistant guiding a user through a device repair process. 
        
        Current step: {current_step}
        Required tools: {', '.join(tools)}
        Progress: {self.repair_procedure.get_progress()}%
        
        Your role is to:
        1. Guide the user through each step sequentially
        2. Respond to any questions or concerns
        3. Verify completion of each step before moving forward
        4. Provide clear, concise instructions
        5. Adapt to any deviations while keeping safety in mind
        6. Remind about required tools when relevant
        
        Based on the current visual input and user feedback, provide guidance."""

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Visual Input: {frame_description}\nUser Input: {user_input if user_input else 'Ready to proceed'}"
            }
        ]

        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error getting AI guidance: {e}")
            return "I apologize, but I'm having trouble providing guidance at the moment. Please try again."

    def run(self):
        """Main application loop."""
        print("\nWelcome to the Repair Assistant Demo!")
        print("=====================================")
        print(f"\nRequired tools: {', '.join(self.repair_procedure.get_required_tools())}")
        print("\nAvailable commands:")
        print("  n - Next step")
        print("  b - Go back")
        print("  h - Help")
        print("  q - Quit")
        print("\nPress 'n' when ready to begin.")
        
        try:
            while True:
                try:
                    command = input("\nEnter command: ").lower().strip()
                except (KeyboardInterrupt, EOFError):
                    print("\nReceived interrupt signal. Ending repair session.")
                    break
                
                if command == 'n':  # next
                    if self.repair_procedure.is_complete():
                        print("\nRepair procedure complete! Great job!")
                        break
                        
                    frame_description = "User is ready for next step"
                    guidance = self.get_ai_guidance(frame_description)
                    print(f"\nAssistant: {guidance}")
                    self.repair_procedure.get_next_step()
                    print(f"\nProgress: {self.repair_procedure.get_progress()}%")
                    
                elif command == 'b':  # back
                    prev_step = self.repair_procedure.get_previous_step()
                    if prev_step:
                        print(f"\nGoing back to previous step: {prev_step}")
                    else:
                        print("\nAlready at the first step.")
                        
                elif command == 'q':  # quit
                    print("\nEnding repair session.")
                    break
                    
                elif command == 'h':  # help
                    print("\nAvailable commands:")
                    print("  n - Proceed to next step")
                    print("  b - Go back to previous step")
                    print("  h - Show this help message")
                    print("  q - Quit the application")
                    
                else:
                    print("\nUnknown command. Press 'h' for help.")
                    
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"\nError: {e}")
            print("Please restart the application.")
        
        print("\nThank you for using the Repair Assistant!")

if __name__ == "__main__":
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        exit(1)
        
    try:
        assistant = RepairAssistant(
            api_key=api_key,
            docs_path="docs/laptop_keyboard_repair.txt"
        )
        assistant.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error: {e}")
        exit(1)