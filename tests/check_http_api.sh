#!/usr/bin/env bash

http http://localhost:20000/motion/config
http http://localhost:20000/motion/cams
http http://localhost:20000/motion/cam/status/0
http http://localhost:20000/telegram/config
# http http://localhost:20000/cb/motion/start/rpi:8080/0
http -f POST http://localhost:20000/cb/motion/picture/upload/rpi:8080/0 image@test.jpg
# http http://localhost:20000/cb/motion/start/0?motion_name=rpi:8080
# http http://localhost:20000/cb/motion/pic/snd/0?motion_name=rpi:8080
# http http://localhost:20000/
