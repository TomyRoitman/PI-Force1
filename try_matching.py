import cv2
import imagehash
import numpy as np
from PIL import Image


def average_hash(image: np.ndarray, hash_size=8, mean=np.mean):
    """
    Average Hash computation

    Implementation follows http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html

    Step by step explanation: https://web.archive.org/web/20171112054354/https://www.safaribooksonline.com/blog/2013/11/26/image-hashing-with-python/

    @image must be a PIL instance.
    @mean how to determine the average luminescence. can try numpy.median instead.
    """
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    # reduce size and complexity, then covert to grayscale
    # image = image.convert("L").resize((hash_size, hash_size), Image.ANTIALIAS)
    image = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), ((hash_size, hash_size)))    # find average pixel value; 'pixels' is an array of the pixel values, ranging from 0 (black) to 255 (white)
    pixels = np.asarray(image)
    avg = mean(pixels)

    # create string of bits
    diff = pixels > avg
    # make a hash
    return imagehash.ImageHash(diff)


# hash0 = imagehash.average_hash(Image.open('football.jpg'))
# hash0 = average_hash(cv2.imread('left_frame.jpg')[437:539, 99: 392])
# hash0 = imagehash.average_hash(Image.open('left_frame.jpg').crop([437, 99, 539, 392]))
im0 = Image.open('left_frame.jpg').crop([437, 99, 539, 392])
hash0 = imagehash.average_hash(Image.open('frame0.jpg'))
# hash0 = imagehash.average_hash(im0)
# im0.show()
# hash0 = average_hash(cv2.imread('football.jpg'))
# hash1 = imagehash.average_hash(Image.open('football2.jpg'))
# hash1 = imagehash.average_hash(Image.open('football2.jpg'))
# hash1 = imagehash.average_hash(Image.open('background.jpg'))
hash1 = imagehash.average_hash(Image.open('frame1.jpg'))
# hash1 = average_hash(cv2.imread('right_frame.jpg')[286:388, 126:421])
# hash1 = imagehash.average_hash(Image.open('right_frame.jpg').crop([286, 126, 388, 421]))
# hash1 = imagehash.average_hash(Image.open('right_frame.jpg'))
# im1 = Image.open('right_frame.jpg').crop([286, 126, 388, 421])
# hash1 = imagehash.average_hash(im1)
# im1.show()
# hash1 = average_hash(cv2.imread('football2.jpg'))
cutoff = 13 # maximum bits that could be different between the hashes.
print(hash0, hash1)
print(hash0 - hash1)
if hash0 - hash1 < cutoff:
    print('images are similar')
else:
    print('images are not similar')



