import sys
sys.path.append(r'C:/Users/XIR1SBY/Desktop/bosch_avp_camera_recorrect/yolo')
import yolo.yolo_main
import Mediapipe_recognize
import cut_face_from_picture
import threading
import time
import cv2

class resource_stack():
    id_stack = []
    YOLO_id = 0
    Mediapipe_id = 0
    cut_picture_id = 0
    successful_checked_ids = []
    
    def change_YOLO_id(self,id):
        self.YOLO_id = id
    
    def Change_Mediapipe_id(self,id):
        self.Mediapipe_id = id
    
    def Change_cut_picture_id(self,id):
        self.cut_picture_id = id
        
    def update_id_stack(self, ids):
        self.id_stack = ids
        
    def return_id(self,index):
        if index >= len(self.id_stack):
            print("error id")
            return -1
        return self.id_stack[index]
    
    def get_len_ids(self):
        return len(self.id_stack)
    
    def add_successful_checked_ids(self,id):
        if self.successful_checked_ids.count(id) > 0:
            return False
        else:
            self.successful_checked_ids.append(id)
    
    def remove_successful_checked_ids(self,id):
        if self.successful_checked_ids.count(id) > 0:
            self.successful_checked_ids.remove(id)
        else:
            return False
            
    def check_successful_checked_ids(self,id):
        if self.successful_checked_ids.count(id) > 0:
            return True
        else:
            return False

class Thread_YOLO (threading.Thread):
    def __init__(self, threadID, name, counter, cap):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.model = yolo.yolo_main.yolo(cap)
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            print("Starting " + self.name)
           # 获得锁，成功获得锁定后返回True
           # 可选的timeout参数不填时将一直阻塞直到获得锁定
           # 否则超时后将返回False
            lockYOLO.acquire()
            global resource_controler
            ids = self.model.get_one_picture()
            resource_controler.update_id_stack(ids)
            # 释放锁
            lockMedia.release()
            print_time(self.name, self.counter)
        
class Thread_Mediapipe (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.model = Mediapipe_recognize.mediapipe_model()
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            print("Starting " + self.name)
           # 获得锁，成功获得锁定后返回True
           # 可选的timeout参数不填时将一直阻塞直到获得锁定
           # 否则超时后将返回False
            lockMedia.acquire()
            global resource_controler
            resource_num = resource_controler.get_len_ids()
            for i in range(resource_num):
                id = resource_controler.return_id(i)
                resource_controler.Change_Mediapipe_id(id)
                flag_checked = self.model.check_feacture(id)
                # 检查是否检测到特征点并且进行管理
                if flag_checked == True:
                    resource_controler.add_successful_checked_ids(id)
                elif flag_checked == False:
                    resource_controler.remove_successful_checked_ids(id)
            # 释放锁
            lockcut.release()
            print_time(self.name, self.counter)
            
class Thread_cut_face (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.model = cut_face_from_picture.cut_face_from_picture()
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while True:
            print("Starting " + self.name)
           # 获得锁，成功获得锁定后返回True
           # 可选的timeout参数不填时将一直阻塞直到获得锁定
           # 否则超时后将返回False
            lockcut.acquire()
            global resource_controler
            resource_num = resource_controler.get_len_ids()
            for i in range(resource_num):
                id = resource_controler.return_id(i)
                if resource_controler.check_successful_checked_ids(id) == False:
                    continue
                resource_controler.Change_cut_picture_id(id)
                self.model.cut_picture(id)
            # 释放锁
            lockYOLO.release()
            print_time(self.name, self.counter)
 
def print_time(threadName, delay):
    time.sleep(delay)
    t = time.time()
    nowTime = int(round(t * 1000))
    print ("%s: %s  ms:%d" % (threadName, time.ctime(time.time()), nowTime))
 
lockYOLO=threading.Lock()
lockMedia=threading.Lock()
lockcut = threading.Lock()
lockMedia.acquire()
lockcut.acquire()
threads = []

cap = cv2.VideoCapture(0)
# 创建新线程
thread1 = Thread_YOLO(1, "Thread-yolo", 0.01, cap)
thread2 = Thread_Mediapipe(2, "Thread-mediapipe", 0.01)
thread3 = Thread_cut_face(3, "Thread-mediapipe", 0.01)

# 创建资源管理
resource_controler = resource_stack()
# 开启新线程
thread1.start()
thread2.start()
thread3.start()
 
# 添加线程到线程列表
threads.append(thread1)
threads.append(thread2)
threads.append(thread3)
for t in threads:
    t.join()
