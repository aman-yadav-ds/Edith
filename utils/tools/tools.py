from langchain.tools import tool

import webbrowser
import subprocess
import psutil, GPUtil

SAFE_APPS = {
    "apex": r"C:\\Program Files\\EA Games\\Apex\\r5apex.exe",
    "wuthering waves": r"C:\\Program Files\\Wuthering Waves\\launcher.exe",
    "arknights": r"C:\\Program Files\\Arknights Endfield\\launcher.exe",
    "obs": r"C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe",
    "code": r"C:\\Users\\ay272\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
}

@tool
def open_website(url: str) -> str:
    """
    Opens a provided URL in the user's default web browser.
    
    WHEN TO USE:
    - ALWAYS use this tool when the user asks to "open", "go to", "search for", or "watch" something on the internet (e.g., YouTube, reading manhwa, checking email).
    - DO NOT use the `execute_terminal` tool to open web pages.
    - DO NOT write Selenium or Python scripts to open browsers unless explicitly asked to write an automation script.
    
    INPUT: A valid, complete URL string (e.g., "https://www.youtube.com/results?search_query=phonk+songs").
    """
    try:
        success = webbrowser.open(url)
        if success:
            return f"Successfully opened website: {url} in the browser."
        else:
            return f"Failed to open website."
    except Exception as e:
        return f"Error opening website: {str(e)}"
    

@tool
def check_vital_signs(action: str) -> str:
    """
    Retrieves real-time hardware diagnostics for the user's system, including CPU, RAM, and GPU usage.
    
    WHEN TO USE:
    - ALWAYS use this tool when the user asks about system health, memory usage, CPU load, overheating, or if the computer is lagging.
    - DO NOT use the `execute_terminal` tool to run task manager or system stat commands.
    
    INPUT: A simple string like 'all', 'cpu', 'ram', or 'gpu'.
    """
    try:
        vitals = []

        cpu_usage = psutil.cpu_percent(interval=1)
        vitals.append(f"CPU Usage: {cpu_usage}%")

        ram = psutil.virtual_memory()
        vitals.append(f"RAM Usage: {ram.percent}% ({ram.used / (1024**3):.2f} GB used of {ram.total / (1024**3):.2f} GB)")

        gpus = GPUtil.getGPUs()
        if gpus:
            for gpu in gpus:
                vitals.append(f"RTX GPU Load: {gpu.load * 100:.1f}%, VRAM: {gpu.memoryUtil * 100:.1f}%, Temp: {gpu.temperature}°C")
        else:
            vitals.append("Dedicated GPU metrics not currently accessible.")

        return " | ".join(vitals)
    except Exception as e:
        return f"Error checking vital signs: {str(e)}"
    

@tool
def launch_application(app_name: str) -> str:
    """
    Launches a specified application from a predefined list of safe apps.
    
    WHEN TO USE:
    - ALWAYS use this tool when the user asks to "open", "launch", or "run" a specific application.
    - DO NOT use the `execute_terminal` tool to launch applications.
    
    INPUT: A string representing the name of the application to launch (e.g., "code", "obs").
    """
    try:
        app_name = app_name.lower()
        if app_name in SAFE_APPS:
            subprocess.Popen(SAFE_APPS[app_name])
            return f"Launching {app_name}..."
        else:
            return f"Application '{app_name}' is not in the list of safe apps."
    except Exception as e:
        return f"Error launching application: {str(e)}"