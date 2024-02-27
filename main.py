import tkinter as tk
from tkinter import scrolledtext, ttk
import g4f
from datetime import datetime, timedelta
import json
import pygame

def ask_gpt(messages: list) -> str:
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_35_turbo,
        messages=messages
    )
    return response

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dias GPT")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="dimgrey")


        pygame.init()
        pygame.mixer.music.load("Medianoche.mp3")
        pygame.mixer.music.play(-1)

        self.animation_label = ttk.Label(root, text="Dias GPT", font=("Helvetica", 36), style="TLabel")
        self.animation_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.animate_label()

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=40, bg="white")
        self.chat_area.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.history_listbox = tk.Listbox(root, width=50, height=30, selectbackground="lightgray")
        self.history_listbox.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.user_input = tk.Entry(root, width=70)
        self.user_input.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.user_input.bind("<Return>", lambda event: self.send_message())

        self.send_button = tk.Button(root, text="Send", command=self.send_message, width=20, height=2, bg="white")
        self.send_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.clear_button = tk.Button(root, text="Clear", command=self.clear_chat_area, width=10, height=1, bg="white")
        self.clear_button.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_application, width=10, height=1, bg="white")
        self.exit_button.grid(row=4, column=0, padx=10, pady=5, sticky="e")

        self.messages = []
        self.loading_label = ttk.Label(root, text="Loading", font=("Helvetica", 12), style="TLabel")
        self.loading_label.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.loading_label.grid_remove()

        self.load_chat_history()
        self.update_chat_area()
        self.update_history_listbox()

        self.loading_animation_frame = 0
        self.loading_animation_speed = 200
        self.loading_animation_text = "Loading"

    def animate_label(self):
        self.animation_label.after(2000, lambda: self.animation_label.config(text="Dias GPT is Initializing"))
        self.animation_label.after(4000, lambda: self.animation_label.config(text="Please wait..."))
        self.animation_label.after(6000, lambda: self.animation_label.grid_remove())

    def send_message(self):
        user_message = self.user_input.get()
        if user_message:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.messages.append({"role": "user", "content": user_message, "timestamp": timestamp})
            self.update_chat_area()
            self.update_history_listbox()
            self.user_input.delete(0, tk.END)

            self.loading_label.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
            self.root.after(100, self.get_assistant_response)

    def get_assistant_response(self):
        self.update_loading_animation()
        assistant_response = ask_gpt(messages=self.messages)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append({"role": "assistant", "content": assistant_response, "timestamp": timestamp})
        self.update_chat_area()
        self.update_history_listbox()

        self.loading_label.grid_remove()

    def update_loading_animation(self):
        dots = '.' * self.loading_animation_frame
        self.loading_label.config(text=f"{self.loading_animation_text} {dots}")
        self.loading_animation_frame = (self.loading_animation_frame + 1) % 4
        self.root.after(self.loading_animation_speed, self.update_loading_animation)

    def update_chat_area(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        for message in self.messages:
            if 'timestamp' in message:
                self.chat_area.insert(tk.END, f"{message['role']} ({message['timestamp']}): {message['content']}\n\n")
            else:
                self.chat_area.insert(tk.END, f"{message['role']}: {message['content']}\n\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def update_history_listbox(self):
        self.history_listbox.delete(0, tk.END)
        for message in self.messages:
            if 'timestamp' in message:
                self.history_listbox.insert(tk.END, f"{message['role']} ({message['timestamp']}): {message['content']}")
            else:
                self.history_listbox.insert(tk.END, f"{message['role']}: {message['content']}")
            self.history_listbox.insert(tk.END, '')

    def clear_chat_area(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)

        self.history_listbox.delete(0, tk.END)

        self.messages = []

    def prune_old_messages(self):
        five_days_ago = datetime.now() - timedelta(days=5)
        self.messages = [message for message in self.messages if 'timestamp' in message and datetime.strptime(message['timestamp'], "%H:%M:%S") >= five_days_ago]

    def save_chat_history(self):
        with open("chat_history.json", "w") as file:
            json.dump(self.messages, file)

    def load_chat_history(self):
        try:
            with open("chat_history.json", "r") as file:
                self.messages = json.load(file)
        except FileNotFoundError:
            pass

    def exit_application(self):
        pygame.mixer.music.stop()
        self.save_chat_history()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ChatApp(root)

    app.update_chat_area()
    app.update_history_listbox()

    root.protocol("WM_DELETE_WINDOW", app.save_chat_history)
    root.mainloop()

if __name__ == "__main__":
    main()
