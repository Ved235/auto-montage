import moviepy as mpy
import os
import pathlib
import subprocess
import random
import shutil

def generateMontage(clip_paths, audio_path, output_path, preset="fast" ,selected_transitions=None):
    clips = sorted([os.path.join(clip_paths,f) for f in os.listdir(clip_paths)])

    if not clips:
        print("No clips found for montage generation.")
        return
    
    temp_dir = pathlib.Path("temp")
    temp_dir.mkdir(exist_ok=True)

    processed_clips = []

    audio = mpy.AudioFileClip(audio_path)
    print(f"Using audio: {audio_path}, duration: {audio.duration} seconds")

    firstClip = mpy.VideoFileClip(clips[0])
    fps = firstClip.fps if firstClip.fps else 30
    print(f"Using FPS: {fps}")
    dropTime = 8 / fps
    musicTime = 0.0
    
    if selected_transitions and len(selected_transitions) > 0:
        transitionTypes = selected_transitions
        print(f"Using selected transitions: {transitionTypes}")
    else:
        transitionTypes = ['translation','rotation','zoom_in','translation_inv','zoom_out','rotation_inv']
        print("No transitions selected, using default transitions.")

   
    
    firstClip = firstClip.subclipped(0, firstClip.duration - dropTime)
    processed_clips.append(addAudio(firstClip, audio, musicTime))
    musicTime += firstClip.duration

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
            "--max_brightness", "3",
            "--output", str(temp_dir / f"{i}_{i+1}_transition")
        ]

        try:
            subprocess.run(command, check=True)

            if temp_transition.exists():
                print(f"Transition {i} to {i+1} processed successfully.")
                nextClip = mpy.VideoFileClip(clipTwo)

                if i < len(clips) - 2:
                    nextClip = nextClip.subclipped(dropTime, nextClip.duration - dropTime)
                else:
                    nextClip = nextClip.subclipped(dropTime, nextClip.duration)

                temp_transition = mpy.VideoFileClip(str(temp_transition))
                processed_clips.append(addAudio(temp_transition, audio, musicTime))
                musicTime += temp_transition.duration

                nextClip = addAudio(nextClip, audio, musicTime)
                processed_clips.append(nextClip)
                musicTime += nextClip.duration

        except subprocess.CalledProcessError as e:
            print("Error encountered",e)
            shutil.rmtree(temp_dir)
            return
        
    for i, clip in enumerate(processed_clips):
        print(f"Clip {i}: {clip.duration} seconds")
    video = mpy.concatenate_videoclips(processed_clips, method="compose")

    video.write_videofile(output_path, codec="libx264", audio_codec="aac", preset=preset)

    for clip in processed_clips:    
        clip.close()
    video.close()

    # Clean up temporary files
    shutil.rmtree(temp_dir)

def addAudio(clip, audio, timing):

    clipDuration = clip.duration
    musicDuration = audio.duration
    introDuration = 0.5
    
    if timing > musicDuration:
        loopTiming = timing % musicDuration
        music = audio.subclipped(loopTiming, min(loopTiming + clipDuration, musicDuration))
    
    else:
        musicEnd = min(timing + clipDuration, musicDuration)
        music = audio.subclipped(timing, musicEnd)

        if musicEnd > musicDuration:
            remainingDuration = musicEnd - musicDuration
            extendedMusic = mpy.concatenate_audioclips([audio]*(int(remainingDuration / musicDuration) + 1))
            music = extendedMusic.subclipped(timing, timing + clipDuration)
    
    if clip.audio is not None:
        if clipDuration > introDuration:
            introAudio = clip.audio.subclipped(0, introDuration).with_volume_scaled(4.0)
            introMusic = music.subclipped(0, introDuration).with_volume_scaled(0.1)
            remainingMusic = music.subclipped(introDuration).with_volume_scaled(0.7)
           
            introCombined = mpy.CompositeAudioClip([introAudio,introMusic])
            finalCombined = mpy.concatenate_audioclips([introCombined, remainingMusic])
        else:
            finalCombined = mpy.CompositeAudioClip([clip.audio.with_volume_scaled(4), music.with_volume_scaled(0.1)])
    else:
        finalCombined = music.with_volume_scaled(0.7)

    return clip.with_audio(finalCombined)

if __name__ == "__main__":
    clip_paths = "./clips"
    output_path = "./montage.mp4"
    audio_path = "./audio.mp3"

    if not os.path.exists(clip_paths):
        print(f"Clip directory {clip_paths} does not exist.")
    else:
        generateMontage(clip_paths, audio_path , output_path)



