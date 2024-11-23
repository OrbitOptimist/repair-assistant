import cv2
import anthropic
import pyttsx3
import json
import os
import logging
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
        """Initialize and configure the camera."""
        self.camera = cv2.VideoCapture(CAMERA_INDEX)
        if not self.camera.isOpened():
            raise Exception("Could not open camera")
            
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.camera.set(cv2.CAP_PROP_FPS, FPS)
            
    def speak(self, text):
        """Convert text to speech and print it."""
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        
    def capture_frame(self):
        """Capture a frame from the camera."""
        if self.camera is None:
            self.setup_camera()
        
        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Could not capture frame")
            
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
        self.speak("Welcome to the Repair Assistant. I'll guide you through the repair process.")
        self.speak(f"Required tools: {', '.join(self.repair_procedure.get_required_tools())}")
        self.speak("Press 'r' when ready to begin.")
        
        try:
            while True:
                frame = self.capture_frame()
                cv2.imshow('Repair View', frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('r'):  # 'r' for ready/next
                    if self.repair_procedure.is_complete():
                        self.speak("Repair procedure complete! Great job!")
                        break
                        
                    frame_description = self.get_frame_description(frame)
                    guidance = self.get_ai_guidance(frame_description)
                    self.speak(guidance)
                    self.repair_procedure.get_next_step()
                    
                elif key == ord('b'):  # 'b' for back
                    prev_step = self.repair_procedure.get_previous_step()
                    if prev_step:
                        self.speak(f"Going back to previous step. {prev_step}")
                    else:
                        self.speak("Already at the first step.")
                        
                elif key == ord('q'):  # 'q' to quit
                    self.speak("Ending repair session.")
                    break
                    
                elif key == ord('h'):  # 'h' for help
                    self.speak("""Available commands:
                    Press 'r' to proceed to next step
                    Press 'b' to go back to previous step
                    Press 'h' for help
                    Press 'q' to quit""")
                    
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.speak("An error occurred. Please restart the application.")
            
        finally:
            if self.camera is not None:
                self.camera.release()
            cv2.destroyAllWindows()

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
    assistant.run()