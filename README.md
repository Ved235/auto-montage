# Auto Montage Generator 

An automated video montage creation tool that uses a pretrained model from [roboflow](https://roboflow.com/) to detect highlights (kills), extract clips and then merge them into a video montage with audio and transitions.
_Currently only supports valorant._
## Features
- **AI Kill Detection**: Uses YOLO machine learning model to automatically detect kills/highlights in gaming videos
- **Dynamic Transitions**: Multiple transition effects including rotation, zoom, translation and distortion
- **Audio Synchronization**: Seamlessly blends game audio with background music
- **Drag & Drop Interface**: User-friendly GUI with drag-and-drop file support
- **Customizable Settings**: Adjustable presets, transition effects and intro duration

## Behind the scenes 

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Video Input    │────▶│  Kill Detection │────▶│  Clip Extraction│
│                 │     │  (YOLO)         │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Final Video    │◀────│  Audio Mixing   │◀────│  Add Transitions│
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```
![image](https://github.com/user-attachments/assets/46e116c6-b985-46c2-8040-055c98cb1395)

## Installation
### Setup
You can either clone the entire repository or download the essential files straight from the release section. Now it also supports install from testpyPi.
#### testpyPi
It can be installed through the use of [uv](https://docs.astral.sh/uv/). Please ensure the virtual enviornment has python >=3.12

```bash
uv venv
uv pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pymontage
auto-montage
```

#### Source
```bash
git clone https://github.com/Ved235/auto-montage.git
cd auto-montage
pip install -r requirements.txt
```

1. Select the input files (video and audio) and select the output path.
2. You can tweak advance settings to choose different transitions and export settings.

File types supported:
- Video files:  ```.mp4, .mov, .mkv```
- Audio files:  ```.mp3, .wav, .m4a```

```
auto-montage/
├── main.py                 # Main GUI application
├── model.pt               # YOLO model for kill detection
├── transition.py          # Video transition effects engine
├── requirements.txt       # Python dependencies
├── src/
│   ├── clipsExtraction.py    # Video clip extraction logic
│   ├── killDetection.py     # AI-powered kill detection
│   └── videoGeneration.py   # Montage generation engine
├── test_files/
│   ├── audio.mp3           # Sample audio file
│   └── input_video.mp4     # Sample video file
└── README.md
```


**Credits:**
https://github.com/salaheddinek/video-editing-py-script/
