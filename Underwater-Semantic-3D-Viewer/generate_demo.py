import argparse
import cv2
import os
import re
import sys
import csv

def main():
    parser = argparse.ArgumentParser(description='Extract frames from all videos in a directory with per-video start/end times')
    parser.add_argument('input_dir', type=str, help='Directory containing video files')
    parser.add_argument('--fps', type=float, default=4.0, help='Frame extraction rate (default: 4.0)')
    parser.add_argument('--config', type=str, default=None, 
                        help='CSV file with per-video start/end times (format: filename,start,end, 1-3 columns)')
    parser.add_argument('--num_frames', type=int, default=80, help='Number of frames to extract (1-80, default: 80)')
    parser.add_argument('--start', type=float, default=0.0, help='Global start time in seconds (default: 0)')
    parser.add_argument('--end', type=float, default=None, help='Global end time in seconds (default: end of video)')
    args = parser.parse_args()

    # Validate input directory
    if not os.path.isdir(args.input_dir):
        raise NotADirectoryError(f"Input directory not found: {args.input_dir}")

    # Validate num_frames
    if args.num_frames < 1 or args.num_frames > 80:
        raise ValueError(f"num_frames must be between 1 and 80 (got {args.num_frames})")

    # Determine base output directory
    base_dir = "/homes/wctsead/semantic_slam/data/demo"
    os.makedirs(base_dir, exist_ok=True)
    
    # Find existing demo directories
    pattern = re.compile(r'demo(\d+)-images')
    existing_dirs = [
        d for d in os.listdir(base_dir) 
        if os.path.isdir(os.path.join(base_dir, d)) and pattern.match(d)
    ]
    
    # Determine next demo directory number
    if existing_dirs:
        max_num = max(int(pattern.match(d).group(1)) for d in existing_dirs)
        next_num = max_num + 1
    else:
        next_num = 0

    # Process all video files in the input directory
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'}
    video_files = []
    
    for filename in os.listdir(args.input_dir):
        if os.path.splitext(filename)[1].lower() in video_extensions:
            video_files.append(os.path.join(args.input_dir, filename))
    
    if not video_files:
        print(f"No video files found in {args.input_dir}")
        sys.exit(0)
    
    print(f"Found {len(video_files)} video files to process")
    
    # Read config file if provided (handles 1-3 columns)
    config = {}
    if args.config:
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Config file not found: {args.config}")
        
        with open(args.config, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 1:
                    continue  # Skip empty rows
                
                filename = row[0].strip()
                # Handle different column counts
                if len(row) == 1:
                    # Only filename - use global start/end
                    config[filename] = (None, None)
                elif len(row) == 2:
                    # Filename and start - use global end
                    try:
                        start = float(row[1].strip())
                        config[filename] = (start, None)
                    except ValueError:
                        print(f"Warning: Invalid start value for {filename} in config file")
                elif len(row) >= 3:
                    # Filename, start, end
                    try:
                        start = float(row[1].strip())
                        end = float(row[2].strip())
                        config[filename] = (start, end)
                    except ValueError:
                        print(f"Warning: Invalid time values for {filename} in config file")
        
        print(f"Loaded config from {args.config} with {len(config)} entries")

    # Process each video
    for video_path in video_files:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        new_dir = f"demo{next_num}-images"
        output_dir = os.path.join(base_dir, new_dir)
        
        # Determine actual start/end values based on priority:
        # 1. CSV config values if specified
        # 2. Global values otherwise
        start_sec = args.start
        end_sec = args.end
        
        if video_name in config:
            start_config, end_config = config[video_name]
            if start_config is not None:
                start_sec = start_config
            if end_config is not None:
                end_sec = end_config
        
        # Open video with OpenCV
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            print(f"  Error: Could not open video: {video_path}")
            continue
        
        # Get video properties
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = video.get(cv2.CAP_PROP_FPS)
        
        # Handle invalid fps
        if video_fps <= 0:
            video_fps = 30.0
        
        total_duration = total_frames / video_fps
        
        # Validate and adjust start/end times
        start_sec = max(0.0, min(start_sec, total_duration))
        
        if end_sec is None or end_sec > total_duration:
            end_sec = total_duration
        else:
            end_sec = max(start_sec, min(end_sec, total_duration))
        
        # Calculate segment boundaries
        start_frame = int(round(start_sec * video_fps))
        end_frame = int(round(end_sec * video_fps))
        segment_frames = end_frame - start_frame
        
        # Ensure segment has at least 1 frame
        if segment_frames < 1:
            end_frame = start_frame + 1
            segment_frames = 1
        
        # Calculate number of frames to extract based on requested FPS
        segment_duration = end_sec - start_sec
        max_frames_for_fps = int(segment_duration * args.fps)
        num_frames = min(args.num_frames, segment_frames, max_frames_for_fps)
        
        # Ensure at least 1 frame if segment has frames
        if num_frames < 1 and segment_frames > 0:
            num_frames = 1
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nProcessing {video_path} -> {output_dir}")
        print(f"  Parameters: start={start_sec}s, end={end_sec}s, fps={args.fps}, num_frames={num_frames}")
        
        # Check if we have frames to extract
        if num_frames <= 0:
            print(f"  Warning: No frames to extract for {video_path}")
            continue
        
        # Calculate step size for even spacing based on desired FPS
        if num_frames > 1:
            step = segment_frames / (num_frames - 1)  # Use n-1 for even spacing
        else:
            step = 0
        
        # Extract frames from clipped segment
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        for i in range(num_frames):
            frame_index = start_frame + int(round(i * step))
            # Ensure frame index is within bounds
            frame_index = min(frame_index, end_frame - 1)
            
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = video.read()
            
            if not ret:
                print(f"  Warning: Could not read frame at {frame_index}")
                continue
                
            frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
            success = cv2.imwrite(frame_path, frame)
            
            if not success:
                print(f"  Warning: Could not write frame {frame_path}")
            else:
                print(f"    Saved frame {i+1}/{num_frames} at {frame_index} (time: {frame_index/video_fps:.2f}s)")
        
        # Close video
        video.release()
        print(f"  Saved {num_frames} frames to {output_dir}")
        
        # Increment the demo number for the next video
        next_num += 1

if __name__ == "__main__":
    main()