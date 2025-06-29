import dearpygui.dearpygui as dpg
import threading
import multiprocessing
import time
from src.videoGeneration import generateMontage
from src.clipsExtraction import extractClips
import shutil
import os
import psutil
import DearPyGui_DragAndDrop as dpg_dnd

def montage_task(input_path, audio_path, output_path, preset="fast", selected_transitions=None, introDuration=0.5):
    temp_dir = "./temp_clips"
    try:
        extractClips(input_path, output_dir=temp_dir)
        generateMontage(temp_dir, audio_path, output_path, preset, selected_transitions, introDuration)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

class AutoMontageGUI:
    def __init__(self):
        self.inputPath = ""
        self.audioPath = ""
        self.outputPath = ""
        self.processing = False
        self.timeElapsed = 0
        self.timerActive = False
        self.current_process = None
        self.cancel_requested = False
        self.preset = "fast"
        self.introDuration = 0.5

        dpg.create_context()
        dpg_dnd.initialize()
        self.setup_gui()
        dpg_dnd.set_drop(self.drop_handler)
        dpg_dnd.set_drag_enter(self.drop_hover)
    
    def setup_gui(self):
        with dpg.window(width=800, height=400, tag="main_window"):
            dpg.add_text("Auto Montage Generator")
            dpg.add_separator()

            with dpg.group():
                dpg.add_text("Input Settings:")

                with dpg.group(horizontal=True):
                    dpg.add_text("Raw Input Path:")
                    dpg.add_input_text(tag="input_path", width=550, default_value="", callback=self.update_input_path)
                    dpg.add_button(label="Browse", tag="browse_input_btn", callback=self.browse_input)
               
                with dpg.group(horizontal=True):
                    dpg.add_text("Audio Path:")
                    dpg.add_input_text(tag="audio_path", width=550, default_value="", callback=self.update_audio_path)
                    dpg.add_button(label="Browse", tag="browse_audio_btn", callback=self.browse_audio)

                with dpg.group(horizontal=True):
                    dpg.add_text("Output Path:")
                    dpg.add_input_text(tag="output_path", width=550, default_value="", callback=self.update_output_path)
                    dpg.add_button(label="Browse", tag="browse_output_btn", callback=self.browse_output)

            dpg.add_separator()

            with dpg.collapsing_header(label="Advanced Settings", default_open=False):
                with dpg.group(horizontal=True):
                    dpg.add_text("Preset:")
                    dpg.add_combo(["ultrafast","fast", "medium", "slow" , "veryslow"], default_value="fast", tag="preset_combo", callback=lambda s, a: setattr(self, 'preset', a))
                
                dpg.add_separator()

                with dpg.group():
                    dpg.add_text("Transition Effects:")
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label="Translation", tag="translation_checkbox", default_value=True)
                        dpg.add_checkbox(label="Rotation", tag="rotation_checkbox", default_value=True)
                        dpg.add_checkbox(label="Zoom In", tag="zoom_in_checkbox", default_value=True)
                        dpg.add_checkbox(label="Translation Inverse", tag="translation_inv_checkbox", default_value=True)
                        dpg.add_checkbox(label="Zoom Out", tag="zoom_out_checkbox", default_value=True)
                        dpg.add_checkbox(label="Rotation Inverse", tag="rotation_inv_checkbox", default_value=True)

                dpg.add_input_float(label="Intro duration (seconds)", tag="intro_duration", default_value=0.5, min_value=0.2, max_value=1)
            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_button(label="Generate Montage", tag="generate_btn", callback=self.start_processing, width=200, height=40)
                dpg.add_button(label="Cancel", tag="cancel_btn", callback=self.cancel_processing, width=200, height=40)

            dpg.add_text(tag="time_elapsed", default_value="Time Elapsed: 0s")

            with dpg.group():
                dpg.add_text("Log Output:")
                dpg.add_input_text(tag="log_output", multiline=True, width=600, height=300, readonly=True, default_value="")
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
            dpg.add_text("", tag="success_details")
            dpg.add_button(label="OK", width=100, callback=lambda: dpg.hide_item("success_modal"))

        with dpg.window(label="Error", modal=True, show=False, tag="error_modal", width=400, height=100, pos=[200, 200]):
            dpg.add_text("An error occurred during montage generation:", color=[255, 100, 100])
            dpg.add_separator()
            dpg.add_input_text(tag="error_message", multiline=True, readonly=True, width=450, height=150)
            dpg.add_button(label="OK", width=100, callback=lambda: dpg.hide_item("error_modal"))
    
    def drop_handler(self, data, keys):
        if data and len(data) > 0:
            file_path = data[0]
            file_ext = os.path.splitext(file_path)[1].lower()
        
            video_extensions = ['.mp4', '.mov', '.mkv', '.m4v']
            audio_extensions = ['.mp3', '.wav', '.m4a']
            
            if file_ext in video_extensions:
                self.inputPath = file_path
                dpg.set_value("input_path", self.inputPath)
                self.log_message(f"Video file dropped: {file_path}")
            elif file_ext in audio_extensions:
                self.audioPath = file_path
                dpg.set_value("audio_path", self.audioPath)
                self.log_message(f"Audio file dropped: {file_path}")
            else:
                self.log_message(f"Unsupported file type: {file_ext}")

    def drop_hover(self, data, keys):
        if data and len(data) > 0:
            file_path = data[0]
            file_ext = os.path.splitext(file_path)[1].lower()
        
            video_extensions = ['.mp4', '.mov', '.mkv', '.m4v']
            audio_extensions = ['.mp3', '.wav', '.m4a']
            
            if file_ext not in video_extensions and file_ext not in audio_extensions:
                self.log_message(f"Unsupported file type: {file_ext}")

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

    def get_transitions(self):
        transitions = []
        
        if dpg.get_value("translation_checkbox"):
            transitions.append("translation")
        if dpg.get_value("rotation_checkbox"):
            transitions.append("rotation") 
        if dpg.get_value("zoom_in_checkbox"):
            transitions.append("zoom_in")
        if dpg.get_value("translation_inv_checkbox"):
            transitions.append("translation_inv")
        if dpg.get_value("zoom_out_checkbox"):
            transitions.append("zoom_out")
        if dpg.get_value("rotation_inv_checkbox"):
            transitions.append("rotation_inv")
            
        return transitions if transitions else ["rotation", "zoom_in", "translation"]

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

    def cancel_processing(self):
        if not self.processing:
            print("No processing in progress to cancel.")
            return
        
        self.cancel_requested = True
        dpg.configure_item("generate_btn", enabled=False, label="Cancelling...")
        dpg.configure_item("cancel_btn", enabled=False)
        self.log_message("Cancelling montage generation...")

        if self.current_process and self.current_process.is_alive():
            try:
                parent = psutil.Process(self.current_process.pid)
                for child in parent.children(recursive=True):
                    self.log_message(f"Terminating child process: {child.pid}")
                    child.terminate()
                self.log_message("Subproces terminated.")

                psutil.wait_procs(parent.children(recursive=True), timeout=3)
                parent.terminate()
            except Exception as e:
                self.log_message(f"Error while terminating process: {str(e)}")

            if os.path.exists("./temp_clips"):
                shutil.rmtree("./temp_clips")
                self.log_message("Temporary clips directory removed.")
        self.reset()
        self.show_success_modal("Montage generation succcessfully cancelled.")

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
        self.cancel_requested = False
        
        self.clear_log()

        self.timer_callback()  

        dpg.configure_item("generate_btn", enabled=False, label="Generating...")
        dpg.configure_item("cancel_btn", enabled = True)
        selected_transitions = self.get_transitions()
        self.introDuration = dpg.get_value("intro_duration")
        self.log_message("Starting montage generation...")
        self.log_message(f"Input Path: {self.inputPath}")
        self.log_message(f"Audio Path: {self.audioPath}")
        self.log_message(f"Output Path: {self.outputPath}")
        self.log_message(f"Preset: {self.preset}")
        self.log_message(f"Selected Transitions: {selected_transitions}")
        self.log_message(f"Intro Duration: {self.introDuration} seconds")
        self.log_message("-" * 50)
      
        self.current_process = multiprocessing.Process(target=montage_task, args=(self.inputPath, self.audioPath, self.outputPath, self.preset, selected_transitions,self.introDuration))
        self.current_process.start()
        threading.Thread(target=self.watch_process, daemon=True).start()

    def watch_process(self):
        self.current_process.join()  

        if self.cancel_requested:
            self.log_message("Process was cancelled.")
        else:
            self.log_message("Process completed successfully.")
            self.show_success_modal(f"Montage generated at: {self.outputPath}")

            os.startfile(self.outputPath)

        self.reset()

    def reset(self):
        self.processing = False
        self.timerActive = False
        self.current_process = None

        dpg.configure_item("generate_btn", enabled=True, label="Generate Montage")
        dpg.configure_item("cancel_btn", enabled=True, label="Cancel")

    def run(self):

        dpg.create_viewport(title='Auto Montage Generator', width=800, height=650)
        dpg.setup_dearpygui()

        dpg.set_primary_window("main_window", True)
        
        dpg.show_viewport()
        dpg.start_dearpygui()
        
        dpg.destroy_context()

if __name__ == "__main__":
    gui = AutoMontageGUI()
    gui.run()
