import asyncio
import os
import threading
import customtkinter as ctk

# Your existing imports
from src.audio_input import AudioInput
from src.llm_engine import Brain
from src.audio_output import AudioOutput

class EdithUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EDITH - Command Center")
        self.geometry("700x600")
        ctk.set_appearance_mode("dark")
        
        # --- State Variables ---
        self.current_mode = "text"
        self.loop = asyncio.new_event_loop()
        self.ui_input_queue = asyncio.Queue()
        
        # --- UI Layout ---
        self.status_label = ctk.CTkLabel(self, text="Status: Booting Up...", font=("Orbitron", 14, "bold"), text_color="orange")
        self.status_label.pack(pady=10)
        
        self.chat_box = ctk.CTkTextbox(self, width=650, height=400, state="disabled")
        self.chat_box.pack(pady=10)
        
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, fill="x", padx=20)
        
        self.text_entry = ctk.CTkEntry(self.input_frame, width=450, placeholder_text="Type a message to Edith...")
        self.text_entry.pack(side="left", padx=10)
        self.text_entry.bind("<Return>", self.send_text)
        
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", width=80, command=self.send_text)
        self.send_button.pack(side="left", padx=5)
        
        self.mode_button = ctk.CTkButton(self.input_frame, text="Mode: TEXT", width=100, command=self.toggle_mode)
        self.mode_button.pack(side="left", padx=5)

        # --- Start Edith Core in Background ---
        # We start your logic in a daemon thread so it closes when the window closes
        self.logic_thread = threading.Thread(target=self.start_background_loop, daemon=True)
        self.logic_thread.start()

    # --- UI Helper Methods ---
    def thread_safe_append(self, sender, text):
        """Updates the chat box safely from the background thread."""
        def update():
            self.chat_box.configure(state="normal")
            self.chat_box.insert("end", f"{sender}: {text}\n\n")
            self.chat_box.see("end")
            self.chat_box.configure(state="disabled")
        self.after(0, update)

    def update_status(self, text, color="white"):
        """Updates the status label safely."""
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    # --- User Interactions ---
    def send_text(self, event=None):
        text = self.text_entry.get().strip()
        if text:
            self.thread_safe_append("Boss", text)
            self.text_entry.delete(0, "end")
            # Send text to the asyncio loop running in the background thread
            self.loop.call_soon_threadsafe(self.ui_input_queue.put_nowait, text)

    def toggle_mode(self):
        if self.current_mode == "text":
            self.current_mode = "voice"
            self.mode_button.configure(text="Mode: VOICE", fg_color="green")
            self.loop.call_soon_threadsafe(self.ui_input_queue.put_nowait, "voice")
        else:
            self.current_mode = "text"
            self.mode_button.configure(text="Mode: TEXT", fg_color="#1f538d") # Default CTk blue
            self.loop.call_soon_threadsafe(self.ui_input_queue.put_nowait, "text")

    # --- The Edith Core Logic ---
    def start_background_loop(self):
        """Sets up the event loop for the background thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.edith_main_loop())

    async def edith_main_loop(self):
        """Your exact logic, modified to talk to the UI."""
        self.update_status("Status: Agent is locked and loaded! ✅", "green")
        MODE = "text"
        
        stop_speaking_event = asyncio.Event()
        
        audio_input = AudioInput(stop_speaking_event)
        llm_engine = Brain()
        audio_output = AudioOutput(stop_speaking_event)
        
        await audio_input.start()
        await audio_output.start()
        
        while True:
            self.update_status("Status: Listening...", "cyan")
            
            # 1. LISTEN
            if MODE == "text":
                # Wait for the UI button instead of CLI input
                user_text = await self.ui_input_queue.get()
            else:
                # In Voice mode, we listen to BOTH the Mic and the UI Queue
                # (In case you click the "Text" button while it's listening to the mic)
                voice_task = asyncio.create_task(audio_input.text_queue.get())
                ui_task = asyncio.create_task(self.ui_input_queue.get())
                
                done, pending = await asyncio.wait([voice_task, ui_task], return_when=asyncio.FIRST_COMPLETED)
                
                if voice_task in done:
                    payload = voice_task.result()
                    user_text = payload["text"]
                    self.thread_safe_append("Boss (Mic)", user_text)
                else:
                    user_text = ui_task.result()
                
                # Cancel whichever task didn't finish
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
                self.update_status("Status: Shutting Down...", "red")
                self.thread_safe_append("EDITH", "Logging Off, Boss.")
                await audio_output.speak("Logging Off. Boss", lambda: None)
                os._exit(0)

            # 2. THINK
            self.update_status("Status: Thinking...", "yellow")
            response_stream = llm_engine.brain_is_braining(
                user_text,
                thread_id="main_thread"
            )
            
            # 3. SPEAK
            self.update_status("Status: Speaking...", "orange")
            self.thread_safe_append("EDITH", "🎙️ [Responding via Audio]")
            
            def on_start_speaking():
                audio_input.is_speaking = True
                stop_speaking_event.clear()
                
            await audio_output.speak(response_stream, on_start_speaking)
            audio_input.is_speaking = False

if __name__ == "__main__":
    app = EdithUI()
    app.mainloop() # This starts the UI