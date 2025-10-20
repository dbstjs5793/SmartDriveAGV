import cv2
import numpy as np
from pymycobot.myagv import MyAgv
import threading
import cv2.aruco as aruco

class AGVController:
    def __init__(self, port, baud_rate):
        self.agv = MyAgv(port, baud_rate)
        self.state = False
        self.direction, self.turn_cnt, self.find_direction = 0, 0, 0
        self.stop = 0
        self.distance = 0
        self.time=0
        self.marker_length = 0.045  

    def process_frame(self, frame):
        height, width, _ = frame.shape
        roi_height = int(height / 3)
        roi_top = height - roi_height
        roi = frame[roi_top:, :]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        img_low_1 = np.array([0,100,100])
        img_upper_1 = np.array([20,255,255])
        img_low_2 = np.array([160,100,100])
        img_upper_2 = np.array([180,255,255])
        
        img_mask_1 = cv2.inRange(hsv,img_low_1,img_upper_1)
        img_mask_2 = cv2.inRange(hsv,img_low_2,img_upper_2)
        red_mask = img_mask_1 + img_mask_2
        
        red_result = cv2.bitwise_and(roi, roi, mask=red_mask)

        gray = cv2.cvtColor(red_result, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) >= 1:
            max_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(max_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                center_line = width // 2
                if cx < center_line - 70:
                    return "LEFT"
                elif cx > center_line + 80:
                    return "RIGHT"
                else:
                    return "FORWARD"
        else : 
            return "LOST"
        
        return None

    def move_forward(self, frame):
        if not self.state:
            self.state = True
            self.find_direction = 0
            self.agv.go_ahead(127, 0.2)
            self.state = False

    def turn_left(self, frame):
        if not self.state:
            self.state = True
            self.direction = 1
            self.turn_cnt = 0
            self.find_direction = 0
            self.agv.counterclockwise_rotation(127, 0.2)
            self.agv.go_ahead(127, 0.2)
            self.state = False

    def turn_right(self, frame):
        if not self.state:
            self.state = True
            self.direction = 2
            self.turn_cnt = 0
            self.find_direction = 0
            self.agv.clockwise_rotation(127, 0.2)
            self.agv.go_ahead(127, 0.2)
            self.state = False

    def lost(self):
        if not self.state:
            self.state = True
            
            # 방향 결정 및 회전
            if self.find_direction == 2:
                self.turn_cnt = 0
                self.direction = 0
                self.agv.stop()
            else:
                rotation_func = self.agv.clockwise_rotation if self.direction == 2 else self.agv.counterclockwise_rotation
                rotation_func(127, 0.3)
                self.turn_cnt += 1
                
                if self.turn_cnt > 3:
                    self.direction = 1 if self.direction == 2 else 2
                    self.turn_cnt = -4
                    self.find_direction += 1

            self.state = False
            
    def stop(self):
        self.agv.stop()
        print("AGV stopped")

    def check(self, frame):
        camera_matrix = np.load(r"Image/camera_matrix.npy")
        dist_coeffs = np.load(r"Image/dist_coeffs.npy")
        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        parameters = aruco.DetectorParameters()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        if ids is not None:
            for i in range(len(ids)):
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners[i], self.marker_length, camera_matrix, dist_coeffs)
                distance = np.linalg.norm(tvec)
                return ids[i][0], distance
        return None, None

    def arugo(self, ids):
        if not self.state:
            self.state = True
            if ids == 0:
                self.agv.pan_left(127, 0.4)
                for i in range(4):
                    self.agv.pan_left(127, 0.2)
                    self.agv.pan_right(127, 0.2)
                self.agv.pan_right(127, 0.4)
                for i in range(4):
                    self.agv.pan_right(127, 0.2)
                    self.agv.pan_left(127, 0.2)
                self.agv.clockwise_rotation(127, 2)
                self.agv.clockwise_rotation(127, 2)
            elif ids == 1:
                self.agv.pan_left(80, 0.68)
                self.agv.go_ahead(127, 1)
                self.agv.pan_right(80, 0.68)
                self.distance = 0.05
                self.direction=2
                self.time=0
            elif ids == 5:
                self.agv.pan_right(80, 0.6)
                self.agv.go_ahead(127, 1.1)
                self.agv.pan_left(80, 1)
            self.state = False

    def camera_thread(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_file = 'agv_video1.avi'
        fps = 30
        cap = cv2.VideoCapture(0)
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Camera error")
                break

            result = self.process_frame(frame)
            maker, dis = self.check(frame)
            if maker is not None:
                text_to_display = str(maker)
            else:
                text_to_display = result

            cv2.putText(frame, text_to_display, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            
            

            if self.stop == 1:
                    if maker == 2 or maker == 4:
                        self.stop = 0
            else:
                if maker is None or (maker in [2, 4]) or (maker is not None and dis > 0.6+self.distance):
                    if result == "LEFT":
                        threading.Timer(0.1+self.time, lambda: self.turn_left(frame)).start()
                    elif result == "RIGHT":
                        threading.Timer(0.1+self.time, lambda: self.turn_right(frame)).start()
                    elif result == "FORWARD":
                        threading.Timer(0.1+self.time, lambda: self.move_forward(frame)).start()
                    else:
                        threading.Timer(0.1+self.time, lambda: self.lost()).start()
                else:
                    if maker == 3:
                        self.time=0.1
                        self.distance=0
                        self.agv.stop()
                        self.stop = 1
                        continue        
                    threading.Timer(0.1, lambda: self.arugo(maker)).start()
                

            out.write(frame)
            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.agv.stop()
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def start(self):
        camera_thread = threading.Thread(target=self.camera_thread)
        camera_thread.start()
        camera_thread.join()

if __name__ == "__main__":
    controller = AGVController("/dev/ttyAMA2", 115200)
    controller.start()
