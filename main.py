import asyncio
import os
import threading
import datetime
import customtkinter as ctk

from src.audio_input import AudioInput
from src.llm_engine import Brain
from src.audio_output import AudioOutput

# --- Futuristic Color Palette ---
BG_COLOR = "#050505"         # Deep abyss black
PANEL_BG = "#111111"         # Slightly lighter for panels
CYAN_GLOW = "#00ffcc"        # Primary HUD text
BLUE_ACCENT = "#0055ff"      # Secondary accent
ALERT_RED = "#ff2a2a"        # For shutdown/errors
WARN_YELLOW = "#ffcc00"      # For processing/thinking
FONT_MAIN = ("Orbitron", 14, "bold") # Assuming you have Orbitron, fallback is Arial
FONT_TERM = ("Consolas", 12)         # Monospace for logs

class EdithUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EDITH - Tactical Command Center")
        self.geometry("800x650")
        self.configure(fg_color=BG_COLOR)
        ctk.set_appearance_mode("dark")
        
        # --- State Variables ---
        self.current_mode = "text"
        self.loop = asyncio.new_event_loop()
        self.ui_input_queue = asyncio.Queue()
        
        # --- UI Layout: HUD Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, border_color=CYAN_GLOW, border_width=1)
        self.header_frame.pack(fill="x", pady=(10, 5), padx=20)
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="E.D.I.T.H. // SYSTEM TERMINAL", font=FONT_MAIN, text_color=CYAN_GLOW)
        self.title_label.pack(side="left", padx=15, pady=10)

        self.status_label = ctk.CTkLabel(self.header_frame, text="[ >_ ] INITIALIZING...", font=FONT_TERM, text_color=WARN_YELLOW)
        self.status_label.pack(side="right", padx=15, pady=10)
        
        # --- UI Layout: Terminal (Chat) ---
        self.chat_box = ctk.CTkTextbox(
            self, 
            width=760, 
            height=450, 
            fg_color="#000000", 
            text_color=CYAN_GLOW, 
            font=FONT_TERM,
            border_color="#333333",
            border_width=1,
            corner_radius=5,
            state="disabled"
        )
        self.chat_box.pack(pady=10, padx=20, expand=True, fill="both")
        
        # --- UI Layout: Command Input ---
        self.input_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.input_frame.pack(pady=(5, 20), fill="x", padx=20)
        
        self.text_entry = ctk.CTkEntry(
            self.input_frame, 
            width=500, 
            placeholder_text="Awaiting command...",
            font=FONT_TERM,
            fg_color=PANEL_BG,
            text_color=CYAN_GLOW,
            border_color=CYAN_GLOW,
            border_width=1,
            corner_radius=4
        )
        self.text_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.text_entry.bind("<Return>", self.send_text)
        
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="EXECUTE", 
            font=FONT_MAIN,
            width=100, 
            fg_color=PANEL_BG,
            hover_color="#1a1a1a",
            border_color=CYAN_GLOW,
            border_width=1,
            text_color=CYAN_GLOW,
            command=self.send_text
        )
        self.send_button.pack(side="left", padx=5)
        
        self.mode_button = ctk.CTkButton(
            self.input_frame, 
            text="[ TXT ]", 
            font=FONT_MAIN,
            width=80, 
            fg_color=PANEL_BG,
            hover_color="#1a1a1a",
            border_color=BLUE_ACCENT,
            border_width=1,
            text_color=BLUE_ACCENT,
            command=self.toggle_mode
        )
        self.mode_button.pack(side="left", padx=5)

        # --- Start Edith Core in Background ---
        self.logic_thread = threading.Thread(target=self.start_background_loop, daemon=True)
        self.logic_thread.start()

    # --- UI Helper Methods ---
    def get_timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def thread_safe_append(self, sender, text, color=None):
        """Updates the chat box safely from the background thread with telemetry formatting."""
        timestamp = self.get_timestamp()
        formatted_message = f"[{timestamp}] [{sender.upper()}] > {text}\n\n"
        
        def update():
            self.chat_box.configure(state="normal")
            self.chat_box.insert("end", formatted_message)
            self.chat_box.see("end")
            self.chat_box.configure(state="disabled")
        self.after(0, update)

    def update_status(self, status_text, color=CYAN_GLOW):
        """Updates the HUD status label safely."""
        def update():
            self.status_label.configure(text=f"[ >_ ] {status_text.upper()}", text_color=color)
            # Add a slight border pulse effect to the header based on status color
            self.header_frame.configure(border_color=color)
        self.after(0, update)

    # --- User Interactions ---
    def send_text(self, event=None):
        text = self.text_entry.get().strip()
        if text:
            self.thread_safe_append("Boss", text)
            self.text_entry.delete(0, "end")
            self.loop.call_soon_threadsafe(self.ui_input_queue.put_nowait, text)

    def toggle_mode(self):
        if self.current_mode == "text":
            self.current_mode = "voice"
            self.mode_button.configure(text="[ MIC ]", text_color=CYAN_GLOW, border_color=CYAN_GLOW)
            self.loop.call_soon_threadsafe(self.ui_input_queue.put_nowait, "voice")
            self.thread_safe_append("SYSTEM", "Audio uplink established. Mic active.")
        else:
            self.current_mode = "text"
            self.mode_button.configure(text="[ TXT ]", text_color=BLUE_ACCENT, border_color=BLUE_ACCENT)
            self.loop.call_soon_threadsafe(self.ui_input_queue.put_nowait, "text")
            self.thread_safe_append("SYSTEM", "Audio uplink severed. Awaiting text input.")

    # --- The Edith Core Logic ---
    def start_background_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.edith_main_loop())

    async def edith_main_loop(self):
        self.update_status("SYSTEM ONLINE", CYAN_GLOW)
        self.thread_safe_append("SYSTEM", "All subsystems nominal. Ready for commands.")
        MODE = "text"
        
        stop_speaking_event = asyncio.Event()
        
        audio_input = AudioInput(stop_speaking_event)
        llm_engine = Brain()
        audio_output = AudioOutput(stop_speaking_event)
        
        await audio_input.start()
        await audio_output.start()
        
        while True:
            self.update_status("AWAITING INPUT", BLUE_ACCENT)
            
            # 1. LISTEN
            if MODE == "text":
                user_text = await self.ui_input_queue.get()
            else:
                voice_task = asyncio.create_task(audio_input.text_queue.get())
                ui_task = asyncio.create_task(self.ui_input_queue.get())
                
                done, pending = await asyncio.wait([voice_task, ui_task], return_when=asyncio.FIRST_COMPLETED)
                
                if voice_task in done:
                    payload = voice_task.result()
                    user_text = payload["text"]
                    self.thread_safe_append("Boss (Mic)", user_text)
                else:
                    user_text = ui_task.result()
                
                for task in pending:
                    task.cancel()

            # Mode Switches
            if user_text.lower() == "voice":
                MODE = "voice"
                continue
            elif user_text.lower() == "text":
                MODE = "text"
                continue

            # Exit Commands
            exit_phrases = ["exit", "shutdown", "shut down", "goodbye", "bye"]
            if any(phrase in user_text.lower() for phrase in exit_phrases):
                self.update_status("SHUTDOWN SEQUENCE INITIATED", ALERT_RED)
                self.thread_safe_append("EDITH", "Logging off. Goodbye, Boss.")
                await audio_output.speak("Logging Off. Boss", lambda: None)
                os._exit(0)

            # 2. THINK
            self.update_status("PROCESSING DATA...", WARN_YELLOW)
            response_stream = llm_engine.brain_is_braining(
                user_text,
                thread_id="main_thread"
            )
            
            # 3. SPEAK
            self.update_status("BROADCASTING", CYAN_GLOW)
            self.thread_safe_append("EDITH", "[ Audio Transmission Originating... ]")
            
            def on_start_speaking():
                audio_input.is_speaking = True
                stop_speaking_event.clear()
                
            await audio_output.speak(response_stream, on_start_speaking)
            audio_input.is_speaking = False

if __name__ == "__main__":
    app = EdithUI()
    app.mainloop()