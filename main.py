import dearpygui.dearpygui as dpg
import threading
import time
from pathlib import Path
from src.videoGeneration import generateMontage
from src.clipsExtraction import extractClips
import shutil
import os

class AutoMontageGUI:
    def __init__(self):
        self.inputPath = ""
        self.audioPath = ""
        self.outputPath = ""
        self.processing = False
        self.timeElapsed = 0
        self.timerActive = False
        self.current_process = None

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
            dpg.add_text(tag="time_elapsed", default_value="Time Elapsed: 0s")

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

        with dpg.window(label="Success", modal=True, show=False, tag="success_modal", width=400, height=150, pos=[200, 200]):
            dpg.add_text("Montage generation completed successfully!", tag="success_message")
            dpg.add_separator()
            dpg.add_text("", tag="success_details")
            dpg.add_button(label="OK", width=100, callback=lambda: dpg.hide_item("success_modal"))

        with dpg.window(label="Error", modal=True, show=False, tag="error_modal", width=400, height=100, pos=[200, 200]):
            dpg.add_text("An error occurred during montage generation:", color=[255, 100, 100])
            dpg.add_separator()
            dpg.add_input_text(tag="error_message", multiline=True, readonly=True, width=450, height=150)
            dpg.add_button(label="OK", width=100, callback=lambda: dpg.hide_item("error_modal"))
            
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
    
    def show_success_modal(self, details=""):
        dpg.set_value("success_details", details)
        dpg.show_item("success_modal")
    
    def show_error_modal(self, error_message):
        dpg.set_value("error_message", error_message)
        dpg.show_item("error_modal")

    def validate_paths(self):
        errors = []
        
        if not self.inputPath:
            errors.append("Input path is required")
        elif not os.path.exists(self.inputPath):
            errors.append("Input file does not exist")
        elif not os.path.isfile(self.inputPath):
            errors.append("Input path must be a file")
    
        if not self.audioPath:
            errors.append("Audio path is required")
        elif not os.path.exists(self.audioPath):
            errors.append("Audio file does not exist")
        elif not os.path.isfile(self.audioPath):
            errors.append("Audio path must be a file")
        
        if not self.outputPath:
            errors.append("Output path is required")
        else:
            output_dir = os.path.dirname(self.outputPath)
            if output_dir and not os.path.exists(output_dir):
                errors.append("Output directory does not exist")
            
        return len(errors) == 0, errors
    
    def clear_log(self):
        dpg.set_value("log_output", "")
    
    def log_message(self, message):
        current_log = dpg.get_value("log_output")
        timestamp = time.strftime("%H:%M:%S")
        new_log = f"[{timestamp}] {message}\n"
        dpg.set_value("log_output", current_log + new_log)

    def timer_callback(self):  
        if not self.timerActive:
            self.timerActive = True
            self.timeElapsed = time.time()
            timer_thread = threading.Thread(target=self.update_timer)
            timer_thread.daemon = True
            timer_thread.start()
        else:
            self.timerActive = False

    def update_timer(self):
        while self.timerActive:
            if self.processing:
                elapsed = time.time() - self.timeElapsed
                dpg.set_value("time_elapsed", f"Time Elapsed: {int(elapsed)}s")
            time.sleep(1)

    def start_processing(self, sender , app_data):
        if self.processing:
            print("Processing already in progress.")
            return

        is_valid, validation_errors = self.validate_paths()
        if not is_valid:
            self.clear_log()
            self.log_message("Validation failed:")
            for error in validation_errors:
                self.log_message(f"  - {error}")
            return
        
        self.processing = True

        self.timer_callback()  
        
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

                success_details = f"Montage generated at: {self.outputPath}"
                self.show_success_modal(success_details)
                self.log_message("Montage generation completed successfully.")

            finally:
                shutil.rmtree("./temp_clips")
                builtins.print = original_print
                self.reset()

        except Exception as e:
            error_message = f"Error during montage generation: {str(e)}"
            self.log_message(error_message)
            self.show_error_modal(error_message)
            self.reset()

    def reset(self):
        self.processing = False
        self.timerActive = False
        self.current_process = None

        dpg.configure_item("generate_btn", enabled=True, label="Generate Montage")

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
