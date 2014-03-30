import urllib
import sys
import os
import random
import string
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

    def setImage(self, image):
        # Set data and create initial pixelated image
        self.originalImage = image
        # "max(w/2,h/2)" finds out how much we have to resize so that
        # only two pixels are visible initially.
        self.pixelSize = max(image.size[0]/2, image.size[1]/2)
        self.currentImage = self.pixelateByCurrentSize()
        self.currentImage.load()

    def depixelate(self, targetPanel):
        # This method generated a less pixelated image from the
        # original and places it into the panel. It should be called
        # from the depixelate button.

        #first, check if we have an image
        if self.originalImage is None or self.currentImage is None:
            print "No image yet."
            return
        
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

def resizeImageToScreen(image, root):
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

    return originalImage

def loadImageIntoPanel(url, root, panel, pixelator, savename):
    print "ok"
    try:
        urllib.urlretrieve(url, savename)
    except IOError:
        print "Could not retrieve URL. (Probably not a direct link)."
        return
    except e:
        print "Unknown error:"
        print e
        return

    print "loading " + url

    image = Image.open(savename)
    # resize image and retrieve new image.
    originalImage = resizeImageToScreen(image, root)
    
    # set the window size so it matches the image. +40 is to account
    # for the buttons. If there is a better way to do this please send
    # me a pull request :)
    root.geometry("%dx%d+%d+%d" % (originalImage.width(),originalImage.height()+40,0,0))

    # get a pixelator instance and initialize it with the image.
    pixelator.setImage(image)

    # pixelate image so the user only sees two pixels.
    pixelated = pixelator.currentImage
    pixelated = ImageTk.PhotoImage(pixelated)
    panel.configure(image = pixelated)
    panel.image = pixelated

def randomFile():
    #loop until we find a filename that's not taken.
    while True:
        filename = ''.join(random.choice(string.lowercase) for i in range(10))
        if not os.path.exists(filename):
            return filename

def main():
    savename = randomFile()

    #prepare window
    root = tk.Tk()
    root.title('NSFL Viewer')
    root.geometry("%dx%d+%d+%d" % (400,200,0,0))
    panel = tk.Label(root)
    panel.pack(side='top', fill='both', expand='yes')

    #put all control elements in a frame
    controlFrame = tk.Frame(root)

    # entry where the user can put URLS
    urlEntry = tk.Entry(controlFrame)
    urlEntry.pack(expand=True, side='left', fill='both')

    # pixelator (image set by load later)
    pixelator = imagePixelatorObj()
    
    # load button
    buttonLoad = tk.Button(controlFrame, text='Load Image',
                           command = lambda: loadImageIntoPanel(urlEntry.get(),
                                                                root, panel,
                                                                pixelator, savename))
    buttonLoad.pack(side='left', fill='x')

    # create depixelation button, set callback for button and pack it
    buttonDepix = tk.Button(controlFrame, text='Depixelate',
                            command = lambda: pixelator.depixelate(panel))
    buttonDepix.pack(side='left', fill='x')
    
    controlFrame.pack(side='top', fill='both')
    # UI finished

    # finally show the pixelated image to the user.
    try:
        root.mainloop()
    except KeyboardInterrupt:
        # If the users kills us via keyboard we do nothing, except
        # removing the NSFL file. Capturing this event might take some
        # time because Tk checks for keyboard interrupts infrequently.
        pass
    except e:
        print "Unknown error:"
        print e
    finally:
        # remove image
        if os.path.exists(savename):
            print "Removing image."
            os.remove(savename)

if __name__ == "__main__":
    main()
