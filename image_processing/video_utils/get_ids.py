import cv2
from os import listdir
from os.path import isfile, join
import subprocess

path = "/dev"
#onlyfiles = [f for f in listdir() if isfile(join(path, f))]
# define the ls command
onlyfiles = []
ls = subprocess.Popen(["ls", "-p", path],
                      stdout=subprocess.PIPE,
                     )
end_of_pipe = ls.stdout
for line in end_of_pipe:
	line = line.decode().split()[0]
	if line.startswith("video"):
		onlyfiles.append(line)
print(onlyfiles)
for file in onlyfiles:
	print(file)
	digit = file[-1]
	if not digit.isdigit():
		continue
	digit = int(digit)
	print(digit, type(digit))
	cap = cv2.VideoCapture(digit)	

	
	ret, frame = cap.read()
	if ret:
		cv2.imwrite(f"cap-{digit}.jpg", frame)

	
