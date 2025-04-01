import webbrowser
import os

report_path = os.path.abspath("hogwarts_report.html")
webbrowser.open('file://' + report_path) 