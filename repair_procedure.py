class RepairProcedure:
    def __init__(self, doc_path):
        self.steps = []
        self.tools = []
        self.troubleshooting = {}
        self.current_step = 0
        self._parse_documentation(doc_path)
    
    def _parse_documentation(self, doc_path):
        """Parse the repair documentation file."""
        current_section = None
        with open(doc_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                if line.lower().startswith('tools required:'):
                    current_section = 'tools'
                elif line.lower().startswith('steps:'):
                    current_section = 'steps'
                elif line.lower().startswith('troubleshooting:'):
                    current_section = 'troubleshooting'
                elif current_section == 'tools' and line.startswith('-'):
                    self.tools.append(line[1:].strip())
                elif current_section == 'steps' and line[0].isdigit():
                    step_num, step = line.split('.', 1)
                    self.steps.append(step.strip())
                elif current_section == 'troubleshooting' and line.startswith('-'):
                    problem, solution = line[1:].strip().split(':', 1)
                    self.troubleshooting[problem.strip()] = solution.strip()
    
    def get_current_step(self):
        """Get the current step description."""
        if 0 <= self.current_step < len(self.steps):
            return f"Step {self.current_step + 1}: {self.steps[self.current_step]}"
        return None
    
    def get_next_step(self):
        """Move to and return the next step."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            return self.get_current_step()
        return None
    
    def get_previous_step(self):
        """Move to and return the previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            return self.get_current_step()
        return None
    
    def get_progress(self):
        """Get the current progress as a percentage."""
        if not self.steps:
            return 0
        return (self.current_step + 1) * 100 // len(self.steps)
    
    def get_required_tools(self):
        """Get the list of required tools."""
        return self.tools
    
    def get_troubleshooting_tip(self, problem):
        """Get troubleshooting tip for a specific problem."""
        return self.troubleshooting.get(problem)
    
    def is_complete(self):
        """Check if the repair procedure is complete."""
        return self.current_step >= len(self.steps) - 1