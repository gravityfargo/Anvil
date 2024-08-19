from PySide6.QtCore import SignalInstance


class EventParser:
    oneshot = False
    debug = False

    def __init__(self, progress_callback: SignalInstance):
        self.progress_callback = progress_callback
        self.default()

    def default(self):
        self.key = ""
        self.text = ""
        self.color = "gray"
        self.charformat = "text"
        self.skip_newline = False

    def emit(self, **kwargs):
        debug_msg = {
            "text": f"{self.key} ",
            "color": "red",
            "charformat": "text",
            "skip_newline": True,
        }
        if self.debug:
            self.progress_callback.emit(debug_msg)

        message = {
            "text": self.text,
            "color": self.color,
            "charformat": self.charformat,
            "skip_newline": self.skip_newline,
        }
        if kwargs.get("text"):
            message["text"] = kwargs["text"]
        if kwargs.get("color"):
            message["color"] = kwargs["color"]
        if kwargs.get("charformat"):
            message["charformat"] = kwargs["charformat"]
        if kwargs.get("skip_newline"):
            message["skip_newline"] = kwargs["skip_newline"]

        self.progress_callback.emit(message)
        self.default()

    def emit_systemctl(self, data: list):
        broke = False
        for line in data:
            if not broke:
                # area before logs
                if not line:
                    broke = True
                line = line.strip().replace("\n", "")

                # status
                if line.startswith("Active: "):
                    line = line.split(" ")
                    if line[1] == "active":
                        self.emit(text=f" {line[1]} ", color="green", skip_newline=True)
                    elif line[1] == "inactive":
                        self.emit(text=f" {line[1]} ", color="yellow", skip_newline=True)
                    else:
                        self.emit(text=f" {line[1]} ", color="red", skip_newline=True)

                    if line[2] == "(running)":
                        self.emit(text=f"{line[2]} ", color="green", skip_newline=True)
                    elif line[2] == "(exited)":
                        self.emit(text=f"{line[2]} ", color="red", skip_newline=True)
                    else:
                        self.emit(text=f"{line[2]} ", color="yellow", skip_newline=True)

                    self.emit(text=" ".join(line[3:]))
                    continue

                self.text = line
                self.emit()
                continue
            if not line:
                continue
            line = line.strip().split(": ")
            self.text = ": ".join(line[2:])
            self.emit()

    def emit_stdout(self, data: list):
        for line in data:
            self.emit(text=line)

    def emit_stderr(self, data: list):
        for line in data:
            self.emit(text=line)
