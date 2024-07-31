from tkinter import Tk
from tkinter.ttk import Progressbar, Checkbutton, Entry, Label, Button
from tkinter.scrolledtext import ScrolledText
from typing import Callable
from browser_handle import authenticate, parse_the_page
from misc import check_browser_state

label_offset = 20


class GUI:
    window: Tk
    input_username: Entry
    input_password: Entry
    auth_button: Button
    auth_label: Label
    parse_button: Button
    progress: Progressbar
    headless: Checkbutton
    inputs: ScrolledText
    outputs: ScrolledText

    def __init__(self):
        self.window = Tk()
        self.window.resizable(False, False)
        self.window.geometry("900x460")
        self.window.configure(bg="#FFFFFF")
        self.window.title("html 2 pdf")
        self._progress_step = 0

        self.input_username = self.get_input("Login", 24, 26, 200, 40)
        self.input_password = self.get_input("Password", 24, 97, 201, 40, password=True)
        self.auth_button, self.auth_label = self.get_button("Authenticate", 24, 177, 200, 38, self.authenticate)
        if check_browser_state('state.json'):
            self.auth_button.configure(state="disabled")
            self.auth_label.configure(text='✅ Already authenticated')
            self.input_username.configure(state="disabled")
            self.input_password.configure(state="disabled")

        self.parse_button, _ = self.get_button("Parse pages", 24, 247, 200, 38, self.parse)
        self.inputs = self.get_text_area("Input URLs (one record - one line, no delimiters)", 235, 26, 650, 200)
        self.progress = Progressbar(self.window, orient="horizontal", length=650, mode="determinate")
        self.progress.place(x=235, y=247)
        self.progress["value"] = 0

        self.outputs = self.get_text_area("Journal", 235, 287, 650, 130)

    def get_input(self, label: str, x: int, y: int, width: int, height: int, password=False) -> Entry:
        lbl = Label(self.window, text=label)
        lbl.place(x=x, y=y, )
        entry = Entry(self.window, show="*" if password else None)
        entry.place(x=x, y=y + label_offset, width=width, height=height)

        return entry

    def get_button(self, label: str, x: int, y: int, width: int, height: int, command: Callable) -> tuple[
        Button, Label]:
        lbl = Label(self.window, text=label)
        lbl.place(x=x, y=y, )
        button = Button(self.window, text=label, command=command)
        button.place(x=x, y=y + label_offset, width=width, height=height)
        return button, lbl

    def get_text_area(self, label: str, x: int, y: int, width: int, height: int) -> ScrolledText:
        lbl = Label(self.window, text=label)
        lbl.place(x=x, y=y, )
        text_area = ScrolledText(self.window)
        text_area.place(x=x, y=y + label_offset, width=width, height=height)
        return text_area

    def authenticate(self):
        username = self.input_username.get()
        password = self.input_password.get()
        status = authenticate(username, password)
        self.auth_label.configure(text=status.message)
        if status.result:
            self.auth_button.configure(state="disabled")

    def parse(self):
        self.parse_button.configure(state="disabled")
        urls = self.inputs.get("1.0", "end-1c").split("\n")
        valid_urls = []
        for url in urls:
            if len(url) == 0:
                continue
            if not url.startswith("http"):
                continue
            valid_urls.append(url)
        self._progress_step = (100 // len(valid_urls)) // 4
        for i, url in enumerate(valid_urls):
            self.outputs.insert("1.0", f"Processing url #{i:02}\n")
            parse_the_page(url, 'output', self.handle_progress)

        self.parse_button.configure(state="enabled")

    def handle_progress(self, message: str, *args, **kwargs):
        self.outputs.insert("1.0", f"{message}\n")
        self.outputs.update()
        self.progress["value"] += self._progress_step


if __name__ == "__main__":
    gui = GUI()
    gui.window.mainloop()
