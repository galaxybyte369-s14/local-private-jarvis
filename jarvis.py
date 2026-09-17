import os
import re
import pyttsx3
import subprocess
import webbrowser
import tkinter as tk
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# --- BACKEND CALIBRATIONS (Copied from your verified engine) ---
def jarvis_speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 185)       
        engine.setProperty('volume', 1.0)     
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
        del engine  
    except Exception as e:
        print(f"[Voice Error]: {e}")

def parse_and_calculate(user_input):
    text = user_input.lower()
    text = text.replace("times", "*").replace("multiply by", "*").replace("x", "*")
    text = text.replace("divided by", "/").replace("divide", "/")
    text = text.replace("plus", "+").replace("add", "+")
    text = text.replace("minus", "-").replace("subtract", "-")
    math_match = re.search(r"([\d\.\s\+\-\*\/\(\)]+)", text)
    if math_match:
        expression = math_match.group(1).strip()
        if any(op in expression for op in ["+", "-", "*", "/"]):
            try:
                result = eval(expression)
                return f"According to my calculation arrays, the exact answer is {result:,}."
            except: pass
    return None

def execute_system_command(user_input):
    text = user_input.lower()
    if "open youtube" in text:
        jarvis_speak("Opening YouTube, sir.")
        webbrowser.open("https://youtube.com")
        return True
    elif "open google" in text:
        jarvis_speak("Opening Google, sir.")
        webbrowser.open("https://google.com")
        return True
    elif "open notepad" in text:
        jarvis_speak("Opening Notepad, sir.")
        subprocess.Popen(["notepad.exe"])
        return True
    elif "open calculator" in text:
        jarvis_speak("Opening Calculator, sir.")
        subprocess.Popen(["calc.exe"])
        return True
    return False

llm = ChatOllama(model="qwen2.5:1.5b", temperature=0.3)
wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

personal_data = ""
if os.path.exists("personal_info.txt"):
    with open("personal_info.txt", "r") as file:
        personal_data = file.read()

def query_brain(user_input):
    math_result = parse_and_calculate(user_input)
    if math_result: return math_result
    if execute_system_command(user_input): return "Action executed successfully, sir."
    
    now = datetime.now()
    system_prompt = f"""You are JARVIS, a highly sophisticated personal butler created by Mr. xyz.
    Today's exact date is {now.strftime('%A, %B %d, %Y')}. Local time is {now.strftime('%I:%M %p')}.
    Always reply as JARVIS. Keep answers brief. No LaTeX code.
    Personal profile context: {personal_data}"""

    context = ""
    if any(k in user_input.lower() for k in ["who is", "what is", "wikipedia"]) and not any(t in user_input.lower() for t in ["date", "time"]):
        try: context = f"\nWikipedia Context:\n{wikipedia_tool.run(user_input)}"
        except: pass

    messages = [SystemMessage(content=system_prompt + context), HumanMessage(content=user_input)]
    return llm.invoke(messages).content


# --- FRONTEND DESIGN (GUI Interface Setup) ---
class JarvisOverlayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS Core")
        self.root.overrideredirect(True)      # Eliminates standard bulky Windows headers
        self.root.attributes("-topmost", True)  # Forces JARVIS to always stay on top of other apps
        self.root.config(bg="#0a0f1d")
        
        # State controller
        self.is_expanded = False
        
        # Build the Compact Round Bubble Interface
        self.bubble = tk.Frame(self.root, bg="#00d2ff", bd=0, width=50, height=50)
        self.bubble.pack_propagate(False)
        self.bubble.pack()
        
        self.lbl_core = tk.Label(self.bubble, text="J", font=("Consolas", 18, "bold"), fg="#0a0f1d", bg="#00d2ff")
        self.lbl_core.pack(fill=tk.BOTH, expand=True)
        
        # Build the Expanded Main Interactive Dashboard Console
        self.panel = tk.Frame(self.root, bg="#0a0f1d", highlightbackground="#00d2ff", highlightthickness=1)
        
        self.chat_history = tk.Text(self.panel, bg="#0f172a", fg="#00d2ff", font=("Consolas", 10), state='disabled', wrap='word', bd=0)
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.input_field = tk.Entry(self.panel, bg="#1e293b", fg="#ffffff", insertbackground="#00d2ff", font=("Consolas", 11), bd=0)
        self.input_field.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.input_field.bind("<Return>", self.process_input)
        
        # Attach drag and toggle controls
        for widget in [self.bubble, self.lbl_core]:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.drag_window)
            widget.bind("<Double-Button-1>", self.toggle_panel)
            
        # Draw initial floating configuration on desktop screen
        self.root.geometry("50x50+100+100")
        jarvis_speak("Systems minimized to desktop overlay, sir.")
        self.root.mainloop()

    def start_drag(self, event):
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()

    def drag_window(self, event):
        self.root.geometry(f"+{event.x_root - self.offset_x}+{event.y_root - self.offset_y}")

    def toggle_panel(self, event=None):
        x, y = self.root.winfo_x(), self.root.winfo_y()
        if not self.is_expanded:
            self.bubble.pack_forget()
            self.panel.pack(fill=tk.BOTH, expand=True)
            self.root.geometry(f"320x450+{x}+{y}")
            self.is_expanded = True
            self.input_field.focus_set()
        else:
            self.panel.pack_forget()
            self.bubble.pack()
            self.root.geometry(f"50x50+{x}+{y}")
            self.is_expanded = False

    def process_input(self, event):
        query = self.input_field.get().strip()
        if not query: return
        if query.lower() in ['quit', 'exit']:
            self.root.destroy()
            return
            
        self.input_field.delete(0, tk.END)
        self.log_to_chat(f"You: {query}\n")
        
        self.root.update() # Force update graphic loop
        response = query_brain(query)
        
        self.log_to_chat(f"JARVIS: {response}\n\n")
        self.root.after(10, lambda: jarvis_speak(response))

    def log_to_chat(self, text):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, text)
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')

if __name__ == "__main__":
    JarvisOverlayApp()
