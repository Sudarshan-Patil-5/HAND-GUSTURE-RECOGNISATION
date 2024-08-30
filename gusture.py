# Step 1: Import Libraries
import cv2
import mediapipe as mp

# Step 2: Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Step 3: Initialize Video Capture
cap = cv2.VideoCapture(0)

# Function to check if finger landmarks are below each other
def is_finger_extended(landmarks, finger_tip_ids, palm_ids):
    return all(landmarks[tip][1] < landmarks[palm][1] for tip, palm in zip(finger_tip_ids, palm_ids))

# Function to check if all fingers are extended
def are_all_fingers_extended(landmarks):
    return (landmarks[4][1] < landmarks[3][1] and  # Thumb
            landmarks[8][1] < landmarks[6][1] and  # Index finger
            landmarks[12][1] < landmarks[10][1] and # Middle finger
            landmarks[16][1] < landmarks[14][1] and # Ring finger
            landmarks[20][1] < landmarks[18][1])  # Little finger

# Step 4: Capture and Process Each Frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Initialize list to store landmark coordinates
            landmark_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                # Get the coordinates
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append([cx, cy])

            # Gesture recognition logic
            gesture = None
            if len(landmark_list) != 0:
                # Check if landmarks are available
                print(f"Landmark list: {landmark_list}")

                # Hi Gesture: Hand open with fingers spread
                if are_all_fingers_extended(landmark_list):
                    gesture = "Hi"
                
                # Thumbs Up Gesture
                elif (landmark_list[4][1] < landmark_list[3][1] and  # Thumb
                      landmark_list[8][1] > landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "Thumbs Up"
                
                # Thumbs Down Gesture
                elif (landmark_list[4][1] > landmark_list[3][1] and  # Thumb
                      landmark_list[8][1] > landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "Thumbs Down"
                
                # OK Gesture
                elif (landmark_list[4][0] < landmark_list[3][0] and  # Thumb
                      landmark_list[8][0] > landmark_list[6][0] and  # Index finger
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "OK"

                # Peace Gesture: Index and middle fingers up, others down
                elif (landmark_list[8][1] < landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] < landmark_list[10][1] and # Middle finger
                      landmark_list[4][1] > landmark_list[3][1] and  # Thumb
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "Peace"
                
                # Fist Gesture: All fingers down
                elif (landmark_list[4][1] > landmark_list[3][1] and  # Thumb
                      landmark_list[8][1] > landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "Fist"

                # Pointing Gesture: Index finger up, others down
                elif (landmark_list[8][1] < landmark_list[6][1] and  # Index finger
                      landmark_list[4][1] > landmark_list[3][1] and  # Thumb
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "Pointing"
                
                # Rock On Gesture: Index and little fingers up, others down
                elif (landmark_list[8][1] < landmark_list[6][1] and  # Index finger
                      landmark_list[20][1] < landmark_list[18][1] and # Little finger
                      landmark_list[4][1] > landmark_list[3][1] and  # Thumb
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1]):  # Ring finger
                    gesture = "Rock On"
                
                # Stop Gesture: Open hand with fingers together
                elif (all(landmark_list[i][1] < landmark_list[i-1][1] for i in range(4, 21, 4)) and # Fingers extended
                      abs(landmark_list[4][1] - landmark_list[3][1]) < 20 and  # Thumb close to palm
                      abs(landmark_list[8][1] - landmark_list[7][1]) < 20 and  # Fingers close together
                      abs(landmark_list[12][1] - landmark_list[11][1]) < 20 and
                      abs(landmark_list[16][1] - landmark_list[15][1]) < 20 and
                      abs(landmark_list[20][1] - landmark_list[19][1]) < 20):
                    gesture = "Stop"

                # Clap Gesture: Hands clapping
                elif (landmark_list[4][1] < landmark_list[3][1] and  # Thumb
                      landmark_list[8][1] < landmark_list[7][1] and  # Index finger
                      landmark_list[12][1] < landmark_list[11][1] and # Middle finger
                      landmark_list[16][1] < landmark_list[15][1] and # Ring finger
                      landmark_list[20][1] < landmark_list[19][1]):  # Little finger
                    gesture = "Clap"

                # Wave Gesture: Hand moving side to side
                elif (abs(landmark_list[8][1] - landmark_list[4][1]) > 50 and  # Index finger
                      abs(landmark_list[8][0] - landmark_list[4][0]) < 30):  # Side-to-side movement
                    gesture = "Wave"

                # Gun Gesture: Index and thumb extended, others down
                elif (landmark_list[4][1] > landmark_list[3][1] and  # Thumb
                      landmark_list[8][1] < landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "Gun"

                # Shaka Gesture: Thumb and little finger extended, others down
                elif (landmark_list[4][1] < landmark_list[3][1] and  # Thumb
                      landmark_list[20][1] < landmark_list[19][1] and # Little finger
                      landmark_list[8][1] > landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1]):  # Ring finger
                    gesture = "Shaka"
                
                # Cross Gesture: Index and middle fingers crossed
                elif (abs(landmark_list[8][0] - landmark_list[12][0]) < 20 and  # Index and middle fingers crossing
                      abs(landmark_list[8][1] - landmark_list[12][1]) < 20):
                    gesture = "Cross"

                # Facepalm Gesture: Palm touching forehead
                elif (abs(landmark_list[0][1] - landmark_list[9][1]) < 50):  # Palm and forehead distance
                    gesture = "Facepalm"

                # Thumbs Side Gesture: Thumb extended sideways, others closed
                elif (landmark_list[4][1] > landmark_list[3][1] and  # Thumb
                      landmark_list[8][1] > landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] > landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "Thumbs Side"
                
                # Double Peace Gesture: Peace sign with both hands
                elif (are_all_fingers_extended(landmark_list) and len(results.multi_hand_landmarks) > 1):
                    gesture = "Double Peace"

                # Finger Guns Gesture: Index and middle fingers extended, others closed
                elif (landmark_list[8][1] < landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] < landmark_list[10][1] and # Middle finger
                      landmark_list[4][1] > landmark_list[3][1] and  # Thumb
                      landmark_list[16][1] > landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] > landmark_list[18][1]):  # Little finger
                    gesture = "Finger Guns"

                # Spider Gesture: All fingers extended
                elif (landmark_list[4][1] < landmark_list[3][1] and  # Thumb
                      landmark_list[8][1] < landmark_list[6][1] and  # Index finger
                      landmark_list[12][1] < landmark_list[10][1] and # Middle finger
                      landmark_list[16][1] < landmark_list[14][1] and # Ring finger
                      landmark_list[20][1] < landmark_list[18][1]):  # Little finger
                    gesture = "Spider"

                # Snap Gesture: Finger and thumb snapping motion
                elif (abs(landmark_list[4][1] - landmark_list[8][1]) < 20 and  # Thumb and index finger snapping
                      abs(landmark_list[4][0] - landmark_list[8][0]) < 20):
                    gesture = "Snap"

                # Display the corresponding text
                if gesture:
                    cv2.putText(frame, gesture, (landmark_list[0][0] - 50, landmark_list[0][1] - 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)
                else:
                    print("No gesture detected")

    # Step 5: Display the Frame
    cv2.imshow('Hand Gesture Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Step 6: Release Resources
cap.release()
cv2.destroyAllWindows()