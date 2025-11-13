import pexpect

shell = pexpect.spawn("zsh", encoding="utf-8")
shell.sendline("cd ..")
shell.sendline("pwd")
shell.expect("\n")  # Wait for output
print("PWD:", shell.before.strip())

# import pexpect
#
# class TestConsole:
#
#     def __init__(self):
#         self.shell = pexpect.spawn("zsh", encoding="utf-8")
#         self.shell.sendline("source ~/.zshrc")
#
#         self.shell.sendline("cd ..")
#         self.shell.sendline("pwd")
#         self.shell.expect("\n")
#         output = self.shell.before
#
#         print(f"output: {output} ...")
#
# if __name__ == "__main__":
#     TestConsole()
#     # app = QApplication(sys.argv)
#     # window = ConsoleWindow()
#     # window.show()
#     # sys.exit(app.exec())