import moviepy as mpy
import os
import pathlib
import subprocess
import random

def generateMontage(clip_paths, output_path):
    clips = sorted([os.path.join(clip_paths,f) for f in os.listdir(clip_paths)])

    if not clips:
        print("No clips found for montage generation.")
        return
    
    temp_dir = pathlib.Path("temp")
    temp_dir.mkdir(exist_ok=True)

    processed_clips = []

    transitionTypes = ['translation','rotation', 'zoom_in', 'translation_inv', 'zoom_out']
    processed_clips.append(mpy.VideoFileClip(clips[0]))

    for i in range(len(clips)-1):
        clipOne = clips[i]
        clipTwo = clips[i+1]

        temp_transition = temp_dir / f"{i}_{i+1}_transition_merged.mp4"
        print(f"Processing transition between {i} and {i+1}")

        transition = random.choice(transitionTypes)

        command = [
            "python", "./transition.py",
            "-i", clipOne, clipTwo,
            "--animation", transition,
            "--num_frames", "8",
            "--merge", "true",
            "--output", str(temp_dir / f"{i}_{i+1}_transition")
        ]

        try:
            subprocess.run(command, check=True)

            if temp_transition.exists():
                print(f"Transition {i} to {i+1} processed successfully.")
                processed_clips.append(mpy.VideoFileClip(str(temp_transition)))
                processed_clips.append(mpy.VideoFileClip(clipTwo))
                
        except subprocess.CalledProcessError as e:
            print(e)
            continue

    for i, clip in enumerate(processed_clips):
        print(f"Clip {i}: {clip.duration} seconds")
    video = mpy.concatenate_videoclips(processed_clips, method="compose")

    video.write_videofile(output_path, codec="libx264")

    for clip in processed_clips:    
        clip.close()
    video.close()

if __name__ == "__main__":
    clip_paths = "./clips"
    output_path = "./montage.mp4"
    if not os.path.exists(clip_paths):
        print(f"Clip directory {clip_paths} does not exist.")
    else:
        generateMontage(clip_paths, output_path)



