"""
Mus3Vid: Music-to-Video Generation Script (version 3-ish)

Pipeline:
1. Load audio file.
2. Generate music description metadata using Gemini 2.5 Flash model.
3. Generate video clips for each section using Gemini's VEO model.
4. Merge generated video clips and overlay the original audio track.
"""

import os
import time
import pickle
import queue
from typing import List, Dict, Any, Tuple
from pydantic_ai import Agent, BinaryContent
from google import genai
from google.genai import types
from moviepy import concatenate_videoclips, VideoFileClip, ColorClip, AudioFileClip

from utils import *

# Initialize Google GenAI client and Gemini model
client = genai.Client(api_key=KEYS["google_gla"])

# Video generation queue
clip_gen_queue: queue.Queue[Tuple[str, str, int]] = queue.Queue()

def save_videos_from_queue(wait_time: int = 5) -> None:
    """
    Process queued video generations using Google's VEO model.
    Downloads generated videos and saves them to disk.

    Args:
        wait_time (int): Time to wait between polling for generation completion.
    """
    generating_video_dict: Dict[str, Any] = {}

    while True:
        # Fill generation queue
        while len(generating_video_dict) < MAX_VIDEOS_GEN:
            if clip_gen_queue.empty():
                break
            prompt, output_file, duration = clip_gen_queue.get()
            if os.path.exists(output_file):
                print(f"[Skip] {output_file} already exists.")
                continue
            print(f"[Queueing] {output_file} ({duration}s)")
            try:
                operation = client.models.generate_videos(
                    model=VEO_MODEL_NAME,
                    prompt=prompt,
                    config=types.GenerateVideosConfig(
                        person_generation="allow_adult" if ALLOW_HUMAN_GENERATION else "dont_allow",
                        aspect_ratio=ASPECT_RATIO,
                        negativePrompt=PROMPTS["vg_negative"],
                        numberOfVideos=1,
                        durationSeconds=duration,
                    ),
                )
                generating_video_dict[output_file] = operation
            except Exception as e:
                print(f"[Error] Generating {output_file}: {e}")
                clip_gen_queue.put((prompt, output_file, duration))
                time.sleep(wait_time)

        # Exit condition
        if len(generating_video_dict) == 0 and clip_gen_queue.empty():
            break

        print(f"[Waiting] {len(generating_video_dict)} in progress, {clip_gen_queue.qsize()} in queue.")
        time.sleep(wait_time)

        # Check if videos are done
        for output_file, operation in list(generating_video_dict.items()):
            operation = client.operations.get(operation)
            if operation.done:
                for n, video in enumerate(operation.response.generated_videos):
                    client.files.download(file=video.video)
                    save_name = output_file if n == 0 else output_file.replace(".mp4", f"_extra{n}.mp4")
                    video.video.save(save_name)
                    print(f"[Saved] {save_name}")
                del generating_video_dict[output_file]

def merge_videos(output_basename: str, clip_durations: List[int], audio_file: str) -> None:
    """
    Merge video clips and overlay the original audio file.

    Args:
        output_basename (str): Base filename for video clips.
        clip_durations (List[int]): List of durations for each clip.
        audio_file (str): Path to the audio file for overlay.
    """
    clips = []
    for idx, duration in enumerate(clip_durations):
        filename = f"{output_basename}_{idx}.mp4"
        if os.path.exists(filename):
            clip = VideoFileClip(filename)
        else:
            print(f"[Missing] {filename}. Using black screen.")
            clip = ColorClip(size=OUTPUT_VIDEO_DIM, color=(0, 0, 0), duration=duration)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    audio_clip = AudioFileClip(audio_file)
    final_clip = final_clip.with_audio(audio_clip)
    final_clip.write_videofile(f"{output_basename}_full.mp4", codec="libx264", audio_codec="aac", fps=24)

    for clip in clips:
        clip.close()

def audio_to_video(audio_file: str, output_folder: str = OUTPUT_FILES_FOLDER) -> None:
    """
    Main pipeline: Generates video from an audio file.

    Args:
        audio_file (str): Path to the input audio file.
        output_folder (str): Folder to save generated videos.
    """
    output_basename = os.path.join(output_folder, os.path.splitext(os.path.basename(audio_file))[0])
    print(f"[Processing] Audio: {audio_file} -> {output_basename}.mp4")

    # Generate or load cached music description
    response_path = f"{output_basename}_response.pkl"
    if os.path.exists(response_path):
        with open(response_path, "rb") as f:
            response = pickle.load(f).output
    else:
        agent = Agent(model=LLM_MODEL, output_type=MusicDescriptionResponse, system_prompt=PROMPTS["llm_system"])
        print("[Generating] Music description...")
        result = agent.run_sync([
            PROMPTS["llm_start_text"],
            BinaryContent(data=open(audio_file, "rb").read(), media_type=f"audio/{audio_file.split('.')[-1]}")
        ])
        response = result.output
        with open(response_path, "wb") as f:
            pickle.dump(result, f)

    # Calculate clip durations
    clip_starts = response.video_clip_start_times + [response.total_duration]
    clip_durations = [min(MAX_CLIP_LEN, clip_starts[i+1] - clip_starts[i]) for i in range(len(clip_starts)-1)]

    # Queue video generations
    for idx, prompt in enumerate(response.video_prompts):
        clip_gen_queue.put((prompt, f"{output_basename}_{idx}.mp4", clip_durations[idx]))

    save_videos_from_queue()
    merge_videos(output_basename, clip_durations, audio_file)

if __name__ == "__main__":
    create_folders()
    if input("Do you want to clean up the output folder? (y/n): ").strip().lower() == "y":
        cleanup()

    # Process all audio files in input folder
    for file in os.listdir(INPUT_FILES_FOLDER):
        if file.endswith((".mp3", ".wav")):
            audio_file = os.path.join(INPUT_FILES_FOLDER, file)
            audio_to_video(audio_file)
        else:
            print(f"[Unsupported] {file}")