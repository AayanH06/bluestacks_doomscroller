import subprocess
import time
from PIL import ImageChops, Image

class DoomScroll:

    def __init__(self, unchanged_count, max_unchanged):
        self.unchanged_count = unchanged_count
        self.max_unchanged = max_unchanged
        self.screen_before = "/sdcard/screen_before.png"
        self.screen_after = "/sdcard/screen_after.png"

    def swipe_down(self):
        subprocess.run(["adb", "shell", "input", "swipe", "500", "2000", "500", "0", "1000"])
        print("***swiping down***\n")
        time.sleep(1.5)

    def tap_button(self, x, y):
        subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])
        print(f"***tapping button @ ({x},{y})***\n")
        time.sleep(2)

    def reset_app(self):
        print("***resetting app***")
        self.tap_button(567,48)
        time.sleep(1.5)
        self.tap_button(310,880)
        print("***reset completed***")
        time.sleep(1)

    def images_are_similar(self, img1_path, img2_path, threshold=5000):
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        if img1.size != img2.size:
            img2 = img2.resize(img1.size)

        if img1.mode != img2.mode:
            img2 = img2.convert(img1.mode)

        diff = ImageChops.difference(img1, img2)
        histogram = diff.histogram()

        diff_sum = sum(i * histogram[i] for i in range(256))

        return diff_sum < threshold

    def doomscroll_behavior(self):
        while True:
            self.swipe_down()

            subprocess.run(["adb", "shell", "screencap", "-p", self.screen_before])
            subprocess.run(["adb", "pull", self.screen_before, "screen_before.png"])

            self.tap_button(1022, 1871)

            self.swipe_down()

            subprocess.run(["adb", "shell", "screencap", "-p", self.screen_after])
            subprocess.run(["adb", "pull", self.screen_after, "screen_after.png"])

            if self.images_are_similar("screen_before.png", "screen_after.png"):
                self.unchanged_count += 1
                print(f"***similar page detected (count: {self.unchanged_count})***")
            else:
                 print("***unique page***")
                 self.unchanged_count = 0

            if self.unchanged_count >= self.max_unchanged:
                print(f"***max unchanged count reached ({self.max_unchanged})***")
                self.reset_app()
                self.unchanged_count = 0
        
if __name__ == "__main__":
    scroller = DoomScroll(0, 2)
    scroller.doomscroll_behavior()