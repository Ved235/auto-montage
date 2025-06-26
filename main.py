import dearpygui.dearpygui as dpg
import threading
import os
import time
from pathlib import Path
from src.videoGeneration import generateMontage
from src.clipsExtraction import extractClips

class AutoMontageGUI:
    def __init__(self):
        self.inputPath = ""
        self.audioPath = ""
        self.outputPath = ""
        self.processing = False

        dpg.create_context()

        self.setup_gui()
    
    def setup_gui(self):
        with dpg.window(width=800, height=400, tag="main_window"):
            dpg.add_text("Auto Montage Generator")
            dpg.add_separator()

            with dpg.group():
                dpg.add_text("Input Settings:")

                with dpg.group(horizontal=True):
                    dpg.add_text("Raw Input Path:")
                    dpg.add_input_text(tag="input_path", width=400, default_value="", callback=self.update_input_path)
                    dpg.add_button(label="Browse", tag="browse_input_btn", callback=self.browse_input)
               
                with dpg.group(horizontal=True):
                    dpg.add_text("Audio Path:")
                    dpg.add_input_text(tag="audio_path", width=400, default_value="", callback=self.update_audio_path)
                    dpg.add_button(label="Browse", tag="browse_audio_btn", callback=self.browse_audio)

                with dpg.group(horizontal=True):
                    dpg.add_text("Output Path:")
                    dpg.add_input_text(tag="output_path", width=400, default_value="", callback=self.update_output_path)
                    dpg.add_button(label="Browse", tag="browse_output_btn", callback=self.browse_output)

            dpg.add_separator()

        with dpg.file_dialog(directory_selector=False, show=False, tag="input_file_dialog", callback=self.update_input_path, width=400):
            dpg.add_file_extension(".mp4")
            dpg.add_file_extension(".avi")
            dpg.add_file_extension(".mov")
        
        with dpg.file_dialog(directory_selector=False, show=False, tag="audio_file_dialog", callback=self.update_audio_path, width=400):
            dpg.add_file_extension(".mp3")
            dpg.add_file_extension(".wav")
        
        with dpg.file_dialog(directory_selector=True, show=False, tag="output_file_dialog", callback=self.update_output_path, width=400):
            dpg.add_file_extension(".mp4")
            dpg.add_file_extension(".avi")
            dpg.add_file_extension(".mov")

    def update_input_path(self, sender, app_data):
        directory = app_data["file_path_name"]
        self.inputPath = directory
        print(f"Input path updated: {self.inputPath}")

    def update_audio_path(self, sender, app_data):
        directory = app_data["file_path_name"]
        self.audioPath = directory
        print(f"Audio path update: {self.audioPath}")

    def update_output_path(self, sender, app_data):
        directory = app_data["file_path_name"]
        self.outputPath = directory
        print(f"Output path updated: {self.outputPath}")

    def browse_input(self, sender, app_data):
        dpg.show_item("input_file_dialog")

    def browse_audio(self, sender, app_data):
        dpg.show_item("audio_file_dialog")

    def browse_output(self, sender, app_data):
        dpg.show_item("output_file_dialog")

    def run(self):

        dpg.create_viewport(title='Auto Montage Generator', width=800, height=600)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        
        dpg.destroy_context()

if __name__ == "__main__":
    gui = AutoMontageGUI()
    gui.run()
    