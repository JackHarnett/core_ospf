# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from core.emulator import coreemu


x= ["jack", "ery", "zxery"]


lines = list(filter(lambda line: "x" in line, x))
print(lines)