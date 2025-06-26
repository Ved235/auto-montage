import os
from moviepy import VideoFileClip
from src.killDetection import detectKills

def extractClips(video_path, output_dir='./temp_clips'):
    gap = 0.5
    buffer = 0.5

    os.makedirs(output_dir, exist_ok=True)
    timestamps = detectKills(video_path)
    if not timestamps:
        print("No kill timestamps detected.")
        return []
    
    timestamps.sort()
    
    group = []
    current_group = [timestamps[0]]

    for i in timestamps[1:]:
        if i - current_group[-1] <= gap:
            current_group.append(i)
        else:
            group.append(current_group)
            current_group = [i]
    group.append(current_group)

    vid = VideoFileClip(video_path)
    duration = vid.duration

    clipPaths = []
    for i, g in enumerate(group):
        start = max(min(g) - buffer, 0)
        end = min(max(g), duration)

        subclip = vid.subclipped(start, end)
        clip_path = os.path.join(output_dir, f'clip_{i}.mp4')
        subclip.write_videofile(clip_path, codec='libx264', audio_codec='aac',fps=vid.fps)
        print(f"Clip {i} saved: {clip_path}")
        clipPaths.append(clip_path)
    vid.close()
    return clipPaths

if __name__ == "__main__":
    video_path = "./test.mp4"
    output_dir = "./clips"
    clip_paths = extractClips(video_path, output_dir)
    print("Extracted clips:", clip_paths)
    

    