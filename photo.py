#!/usr/bin/env python3

import time
import os
from datetime import datetime
from picamera2 import Picamera2

output_dir = 'pictures'
picture_interval = 60 # in seconds

picam2 = Picamera2()
capture_config = picam2.create_still_configuration(raw={}, display=None)
picam2.start()

time.sleep(2) # initial cooldown to let the camera kick in
while True:
  picture = picam2.switch_mode_capture_request_and_stop(capture_config)
  now = datetime.today()
  picture_name = now.strftime(os.path.join('%Y-%m', '%Y-%m-%d-%H-%M-%S.jpg'))
  picture_path = os.path.join(output_dir, picture_name)
  picture_dir = os.path.abspath(os.path.join(picture_path, os.pardir))
  if not os.path.exists(picture_dir):
      os.makedirs(picture_dir)
  picture.save("main", picture_path)
  print('Took and saved picture', picture_path, flush=True)
  time.sleep(picture_interval)
