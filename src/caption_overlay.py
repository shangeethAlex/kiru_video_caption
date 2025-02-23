import cv2

def add_text_captions(video_path, script_path, output_path="output/output_video.mp4"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return
    
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    # Load script file
    with open(script_path, 'r', encoding='utf-8') as file:
        captions = file.readlines()
    
    caption_index = 0
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if caption_index < len(captions):
            text = captions[caption_index].strip()
            frame_count += 1
            
            if frame_count % (fps * 3) == 0:  # Change text every 3 seconds
                caption_index += 1
            
            # Add text overlay
            cv2.putText(frame, text, (50, frame_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (255, 255, 255), 2, cv2.LINE_AA)
        
        out.write(frame)
    
    cap.release()
    out.release()
    print(f"Output video saved as {output_path}")
