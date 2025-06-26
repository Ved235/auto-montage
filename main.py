import dearpygui.dearpygui as dpg
import threading
import time
from pathlib import Path
from src.videoGeneration import generateMontage
from src.clipsExtraction import extractClips
import shutil

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

            dpg.add_button(label="Generate Montage", tag="generate_btn", callback=self.start_processing, width=200, height=40)

            with dpg.group():
                dpg.add_text("Log Output:")
                dpg.add_input_text(tag="log_output", multiline=True, width=600, height=200, readonly=True, default_value="")
                dpg.add_button(label="Clear Log", tag="clear_log_btn", callback=self.clear_log)

        with dpg.file_dialog(directory_selector=False, show=False, tag="input_file_dialog", callback=self.update_input_path, width=400, height=400):
            dpg.add_file_extension(".mp4")
            dpg.add_file_extension(".avi")
            dpg.add_file_extension(".mov")
        
        with dpg.file_dialog(directory_selector=False, show=False, tag="audio_file_dialog", callback=self.update_audio_path, width=400, height=400):
            dpg.add_file_extension(".mp3")
            dpg.add_file_extension(".wav")
        
        with dpg.file_dialog(directory_selector=False, show=False, tag="output_file_dialog", callback=self.update_output_path, width=400, height=400):
            dpg.add_file_extension(".mp4")
            dpg.add_file_extension(".avi")
            dpg.add_file_extension(".mov")

    def update_input_path(self, sender, app_data):
        directory = app_data["file_path_name"]
        self.inputPath = directory
        dpg.set_value("input_path", self.inputPath)
        print(f"Input path updated: {self.inputPath}")

    def update_audio_path(self, sender, app_data):
        directory = app_data["file_path_name"]
        self.audioPath = directory
        dpg.set_value("audio_path", self.audioPath)
        print(f"Audio path update: {self.audioPath}")

    def update_output_path(self, sender, app_data):
        directory = app_data["file_path_name"]
        self.outputPath = directory
        dpg.set_value("output_path", self.outputPath)
        print(f"Output path updated: {self.outputPath}")

    def browse_input(self, sender, app_data):
        dpg.show_item("input_file_dialog")

    def browse_audio(self, sender, app_data):
        dpg.show_item("audio_file_dialog")

    def browse_output(self, sender, app_data):
        dpg.show_item("output_file_dialog")
    
    def clear_log(self):
        dpg.set_value("log_output", "")
    
    def log_message(self, message):
        current_log = dpg.get_value("log_output")
        timestamp = time.strftime("%H:%M:%S")
        new_log = f"[{timestamp}] {message}\n"
        dpg.set_value("log_output", current_log + new_log)

    def start_processing(self, sender , app_data):
        if self.processing:
            print("Processing already in progress.")
            return
        
        if not self.inputPath or not self.audioPath or not self.outputPath:
            print("Please ensure all paths are set before starting the process.")
            return
        
        self.processing = True
        dpg.configure_item("generate_btn", enabled=False, label="Generating...")

        self.clear_log()
        self.log_message("Starting montage generation...")
        self.log_message(f"Input Path: {self.inputPath}")
        self.log_message(f"Audio Path: {self.audioPath}")
        self.log_message(f"Output Path: {self.outputPath}")
        self.log_message("-" * 50)

        thread = threading.Thread(target=self.generate_montage)
        thread.daemon = True
        thread.start()
    
    def generate_montage(self):
        try:
            original_print = print
            def gui_print(*args, **kwargs):
                message = " ".join(map(str, args))
                self.log_message(message)
                original_print(*args, **kwargs)
            
            import builtins
            builtins.print = gui_print

            try:
                self.log_message("Extracting clips from input file.")
                extractClips(self.inputPath, output_dir="./temp_clips")
                self.log_message("Clips extracted successfully.")
                generateMontage("./temp_clips", self.audioPath, self.outputPath)
                dpg.configure_item("generate_btn", enabled=True, label="Generate Montage")
                self.log_message("Montage generation completed successfully.")

            finally:
                shutil.rmtree("./temp_clips")
                builtins.print = original_print
                self.processing = False

        except Exception as e:
            error_message = f"Error during montage generation: {str(e)}"
            self.log_message(error_message)

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
    