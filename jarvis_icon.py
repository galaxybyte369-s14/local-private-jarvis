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

# --- 1. JARVIS SYSTEM BACKEND ---
def jarvis_speak(text):
    """Voice execution block with explicit index tracking to fix list errors"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 185)       
        engine.setProperty('volume', 1.0)     
        voices = engine.getProperty('voices')
        if voices and len(voices) > 0:
            engine.setProperty('voice', voices[0].id) # FIXED: Use index 0 explicitly
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

# Establish local AI connection
llm = ChatOllama(model="qwen2.5:1.5b", temperature=0.3)
wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

personal_data = ""
if os.path.exists("personal_info.txt"):
    with open("personal_info.txt", "r") as file:
        personal_data = file.read()
else:
    personal_data = "The user is Mr. xyz."

def query_jarvis_brain(user_input):
    math_res = parse_and_calculate(user_input)
    if math_res: return math_res
    if execute_system_command(user_input): return "Action executed successfully, sir."
    
    now = datetime.now()
    system_prompt = f"""You are JARVIS, a highly sophisticated, loyal, and intelligent personal butler created by Mr. xyz.
    Today's exact date is {now.strftime('%A, %B %d, %Y')}. Local time is {now.strftime('%I:%M %p')}.
    Always reply as JARVIS. Keep answers brief. No LaTeX code.
    Personal profile context: {personal_data}"""

    context = ""
    if any(k in user_input.lower() for k in ["who is", "what is", "wikipedia"]) and not any(t in user_input.lower() for t in ["date", "time"]):
        try: context = f"\nWikipedia Context:\n{wikipedia_tool.run(user_input)}"
        except: pass

    messages = [SystemMessage(content=system_prompt + context), HumanMessage(content=user_input)]
    return llm.invoke(messages).content


# --- 2. FRONTEND GRAPHICAL PANEL ---
class JarvisUnifiedApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS System")
        self.root.overrideredirect(True)       
        self.root.attributes("-topmost", True)   
        self.root.config(bg="#0a0f1d")
        
        self.is_expanded = False
        
        # Miniature Orb Frame
        self.bubble = tk.Frame(self.root, bg="#00d2ff", width=55, height=55, cursor="hand2")
        self.bubble.pack_propagate(False)
        self.bubble.pack()
        
        self.label = tk.Label(self.bubble, text="J", font=("Consolas", 16, "bold"), fg="#0a0f1d", bg="#00d2ff")
        self.label.pack(fill=tk.BOTH, expand=True)
        
        # Interactive Chat Console Frame
        self.panel = tk.Frame(self.root, bg="#0a0f1d", highlightbackground="#00d2ff", highlightthickness=1)
        
        # Control Header Bar inside the Console Panel
        self.header_bar = tk.Frame(self.panel, bg="#0f172a", height=30)
        self.header_bar.pack(fill=tk.X, side=tk.TOP)
        
        # FIXED: Clickable Close/Minimize Buttons inside the opened console panel
        self.btn_minimize = tk.Button(self.header_bar, text="[ Fold to Bubble ]", font=("Consolas", 9, "bold"), bg="#0f172a", fg="#00d2ff", bd=0, activebackground="#00d2ff", activeforeground="#0a0f1d", command=self.toggle_display)
        self.btn_minimize.pack(side=tk.LEFT, padx=5)

        self.btn_close = tk.Button(self.header_bar, text="[ Close App ]", font=("Consolas", 9, "bold"), bg="#0f172a", fg="#ff4a4a", bd=0, activebackground="#ff4a4a", activeforeground="#ffffff", command=self.shutdown_system)
        self.btn_close.pack(side=tk.RIGHT, padx=5)

        self.chat_history = tk.Text(self.panel, bg="#0f172a", fg="#00d2ff", font=("Consolas", 10), state='disabled', wrap='word', bd=0)
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.input_field = tk.Entry(self.panel, bg="#1e293b", fg="#ffffff", insertbackground="#00d2ff", font=("Consolas", 11), bd=0)
        self.input_field.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.input_field.bind("<Return>", self.send_message)
        
        # Right-click context popup options menu
        self.menu = tk.Menu(self.root, tearoff=0, bg="#0f172a", fg="#00d2ff", activebackground="#00d2ff", activeforeground="#0a0f1d")
        self.menu.add_command(label="Open Assistant Console", command=self.toggle_display)
        self.menu.add_separator()
        self.menu.add_command(label="Shutdown JARVIS completely", command=self.shutdown_system)

        # Mouse configuration paths
        for widget in [self.bubble, self.label]:
            widget.bind("<Button-1>", self.start_drag)         
            widget.bind("<B1-Motion>", self.drag_motion)
            widget.bind("<Button-3>", self.show_popup_menu)     

        self.root.geometry("55x55+1200+400")
        self.root.mainloop()

    def start_drag(self, event):
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()

    def drag_motion(self, event):
        self.root.geometry(f"+{event.x_root - self.offset_x}+{event.y_root - self.offset_y}")

    def show_popup_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def toggle_display(self, event=None):
        """Swaps seamlessly between floating icon bubble and main chat screen panel"""
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
            self.root.geometry(f"55x55+{x}+{y}")
            self.is_expanded = False

    def send_message(self, event):
        query = self.input_field.get().strip()
        if not query: return
        
        # FIXED: Explicit checks inside the input listener to intercept close commands immediately
        if query.lower() in ['exit', 'quit']:
            self.shutdown_system()
            return
        if query.lower() == 'hide':
            self.input_field.delete(0, tk.END)
            self.toggle_display()
            return
            
        self.input_field.delete(0, tk.END)
        self.log_to_interface(f"You: {query}\n")
        self.root.update()
        
        response = query_jarvis_brain(query)
        self.log_to_interface(f"JARVIS: {response}\n\n")
        self.root.after(10, lambda: jarvis_speak(response))

    def log_to_interface(self, text):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, text)
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')

    def shutdown_system(self):
        jarvis_speak("Powering down system grids. Goodbye Mr. xyz.")
        self.root.destroy()

if __name__ == "__main__":
    JarvisUnifiedApp()
