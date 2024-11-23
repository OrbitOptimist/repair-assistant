import cv2
import anthropic
import pyttsx3
import json
import os
from time import sleep

class RepairAssistant:
    def __init__(self, api_key, docs_path):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.engine = pyttsx3.init()
        self.camera = None
        self.current_step = 0
        self.repair_doc = self._load_documentation(docs_path)
        
    def _load_documentation(self, docs_path):
        with open(docs_path, 'r') as f:
            return f.read()
            
    def speak(self, text):
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        
    def capture_frame(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
        
        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Could not capture frame")
        return frame
    
    def get_frame_description(self, frame):
        # Convert frame to base64 for API (simplified for demo)
        _, buffer = cv2.imencode('.jpg', frame)
        return "Image shows user attempting repair step"  # Simplified for demo
        
    def get_ai_guidance(self, frame_description, user_input=None):
        system_prompt = f"""You are a repair assistant guiding a user through a device repair process. 
        You have access to the following repair documentation:
        
        {self.repair_doc}
        
        Current repair progress: Step {self.current_step + 1}
        
        Your role is to:
        1. Guide the user through each step sequentially
        2. Respond to any questions or concerns
        3. Verify completion of each step before moving forward
        4. Provide clear, concise instructions
        5. Adapt to any deviations while keeping safety in mind
        
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

        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=messages
        )
        
        return response.content[0].text

    def run(self):
        self.speak("Welcome to the Repair Assistant. I'll guide you through the repair process. Say 'ready' when you want to begin.")
        
        try:
            while True:
                frame = self.capture_frame()
                cv2.imshow('Repair View', frame)
                
                # For demo, we'll use a simple key press instead of voice input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('r'):  # 'r' for ready/next
                    frame_description = self.get_frame_description(frame)
                    guidance = self.get_ai_guidance(frame_description)
                    self.speak(guidance)
                    self.current_step += 1
                elif key == ord('q'):  # 'q' to quit
                    break
                elif key == ord('h'):  # 'h' for help
                    self.speak("Press 'r' to proceed to next step, 'h' for help, or 'q' to quit.")
                    
        finally:
            if self.camera is not None:
                self.camera.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        exit(1)
        
    assistant = RepairAssistant(
        api_key=api_key,
        docs_path="docs/laptop_keyboard_repair.txt"
    )
    assistant.run()