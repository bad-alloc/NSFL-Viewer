import urllib
import sys
import os
import Tkinter as tk
from PIL import Image, ImageTk

class imagePixelatorObj (object):
    # This class keeps both the unpixelated image as well as the
    # pixelated image. If the user clicks the "depixelate" button,
    # pixelSize is decreased, a new pixelated image is produced from
    # the original image and placed on the panel the user is viewing.
    originalImage = None
    pixelSize = 1
    currentImage = None

    def pixelateByCurrentSize(self):
        # This method generates a pixelated image from the original by
        # copying the original (so no information is lost) and the
        # shrinking it to the desired pixel size. Afterwards its size
        # is increased again. This way we get rid of information in
        # the image and only very large pixels remain.
        image = self.originalImage.copy()
        image = image.resize((image.size[0]/self.pixelSize,
                              image.size[1]/self.pixelSize), Image.NEAREST)
        image = image.resize((image.size[0]*self.pixelSize,
                              image.size[1]*self.pixelSize), Image.NEAREST)
        return image

    def __init__ (self, image, size):
        # Set data and create initial pixelated image
        self.originalImage = image
        self.pixelSize = size
        self.currentImage = self.pixelateByCurrentSize()
        self.currentImage.load()

    def depixelate(self, targetPanel):
        # This method generated a less pixelated image from the
        # original and places it into the panel. It should be called
        # from the depixelate button.
        if self.pixelSize / 2 <= 1:
            self.pixelSize = 1
        else:
            self.pixelSize = self.pixelSize / 2
        self.currentImage = self.pixelateByCurrentSize()
        self.currentImage.load()
        panelImage = ImageTk.PhotoImage(self.currentImage)
        targetPanel.configure(image = panelImage)
        # keep reference, so the GC doesn't immediately remove the image
        targetPanel.image = panelImage 

def main():
    url = ''
    savename = ''
    removeImageAfterView = True

    #get image from the url the user gave us
    if len(sys.argv) > 1 and sys.argv[1] != '':
        url = sys.argv[1]
    else:
        print "Error. No url supplied."
        return

    # check if the user has supplied any place to store the image. If
    # not, we'll remove it after displaying it.
    if len(sys.argv) > 2 and sys.argv[2] != '':
        savename = sys.argv[2]
        removeImageAfterView = False
    else:
        savename = "NSFL.tmp"

    try:
        urllib.urlretrieve(url, savename)
    except(IOError):
        print "Could not retrieve URL"
        return

    #prepare window
    root = tk.Tk()
    root.title('NSFL Viewer')
    image = Image.open(savename)

    #store original since pixelation destroys information
    originalImage = ImageTk.PhotoImage(image)

    #get size info from PhotoImage
    w = originalImage.width()
    h = originalImage.height()
    x = 0
    y = 0

    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()

    #resize image if it's larger than the screen
    if w > screenWidth or h > screenHeight:
        #calculate the aspect ratio for the image
        ratio = min(screenWidth / float(w), screenHeight / float(h));
        #resize image according to the aspect ratio so we fill as much
        #screen as possible while not distorting the image. If we
        #didn't resize large images would only be partially visible.
        image = image.resize((w*ratio, h*ratio),Image.ANTIALIAS)
        #now reload and replace the image and correct the width and height values.
        image.load()
        originalImage = ImageTk.PhotoImage(image)
        w = originalImage.width()
        h = originalImage.height()

    # set the window size so it matches the image
    root.geometry("%dx%d+%d+%d" % (w,h, x, y))
    panel = tk.Label(root, image=originalImage)
    panel.pack(side='top', fill='both', expand='yes')

    # get a pixelator instance and initialize it with the
    # image. "max(w/2,h/2)" finds out how much we have to resize so
    # that only two pixels are visible initially.
    pixelator = imagePixelatorObj(image, max(w/2,h/2))

    # pixelate image so the user only sees two pixels.
    pixelated = pixelator.currentImage
    pixelated = ImageTk.PhotoImage(pixelated)
    panel.configure(image = pixelated)

    # set callback for button and pack it
    buttonDepix = tk.Button(panel, text='Depixelate',
                            command = lambda: pixelator.depixelate(panel))
    buttonDepix.pack(side='top', fill='x')

    # finally show the pixelated image to the user.
    root.mainloop()

    #maybe remove image
    if removeImageAfterView:
        print "Removing image." 
        os.remove(savename)

if __name__ == "__main__":
    main()
