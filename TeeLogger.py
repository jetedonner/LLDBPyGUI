import sys

class TeeLogger:
    def __init__(self, original_stream):
        self.original_stream = original_stream
        self.log = []

    def write(self, message):
        self.log.append(message)
        self.original_stream.write(message)

    def flush(self):
        self.original_stream.flush()

# Redirect stdout
sys.stdout = TeeLogger(sys.stdout)

# Now, anything printed will be logged and displayed
print("Hello, world!")
print("This is a test.")

# Access the log
print("Captured log:")
print("".join(sys.stdout.log))
# print("".join(sys.stdout.log))
