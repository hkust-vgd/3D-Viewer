import cv2
import os

# ---- CONFIGURATION ----
VIDEO_PATH = "/homes/wctsead/semantic_slam/sample/HongKong1_Jun2024_0015.mp4"     # path to your .mov file
OUTPUT_DIR = "/homes/wctsead/semantic_slam/data/demo/demo3-images"        # folder to save extracted images
TARGET_FPS = 4              # frames per second to sample at
MAX_FRAMES = 80              # around 30 images
FILE_PREFIX = ""        # prefix for saved frame files
# ------------------------


def main():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error: Cannot open video file '{VIDEO_PATH}'")
        return

    # Get the original video fps
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    if original_fps == 0:
        print("Error: Could not read video FPS.")
        cap.release()
        return

    # Compute how many frames to skip between each extracted frame
    # to approximate TARGET_FPS (if different from original_fps).
    # If original == TARGET, frame_step ~= 1 (every frame).
    frame_step = max(int(round(original_fps / TARGET_FPS)), 1)

    print(f"Video FPS: {original_fps:.2f}")
    print(f"Extracting at ~{TARGET_FPS} fps (frame_step = {frame_step})")
    print(f"Will stop after saving {MAX_FRAMES} frames.\n")

    saved_count = 0
    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            # End of video
            break

        # Save this frame if it's one of the sampled frames
        if frame_index % frame_step == 0:
            # Build output filename, zero-padded index
            filename = f"{FILE_PREFIX}_{saved_count:03d}.png"
            output_path = os.path.join(OUTPUT_DIR, filename)

            # Save the frame as an image
            cv2.imwrite(output_path, frame)
            print(f"Saved: {output_path}")
            saved_count += 1

            # Stop after reaching MAX_FRAMES
            if saved_count >= MAX_FRAMES:
                print("\nReached target number of frames; stopping.")
                break

        frame_index += 1

    cap.release()
    print(f"Done. Total frames saved: {saved_count}")


if __name__ == "__main__":
    main()