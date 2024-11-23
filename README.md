# AI-Powered Repair Assistant

An interactive repair assistant that uses computer vision and AI to guide users through device repair procedures.

## Features
- Real-time camera input for visual guidance
- AI-powered instructions using Claude API
- Text-to-speech feedback
- Step-by-step repair guidance
- Flexible workflow adaptation
- Documentation-based repair procedures

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export ANTHROPIC_API_KEY='your_api_key_here'
```

3. Run the application:
```bash
python repair_assistant.py
```

## Usage
- Press 'r' to proceed to next step/indicate readiness
- Press 'h' for help
- Press 'q' to quit

## Adding New Repair Procedures
1. Create a new text file in the `docs` directory
2. Follow the format in `laptop_keyboard_repair.txt`
3. Include:
   - Required tools
   - Step-by-step instructions
   - Troubleshooting tips

## Architecture

### Components
1. **Camera Interface**
   - Real-time video capture
   - Frame processing for AI analysis

2. **AI Integration**
   - Claude API for intelligent guidance
   - Context-aware responses
   - Progress tracking

3. **Text-to-Speech**
   - Clear voice instructions
   - Real-time feedback

4. **Documentation Parser**
   - Structured repair guides
   - Progress tracking
   - Step verification

## Future Enhancements
- Voice input support
- Advanced image recognition
- Progress saving/loading
- Multiple language support
- Enhanced error detection
- User authentication
- Analytics and logging