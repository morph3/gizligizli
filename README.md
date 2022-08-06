# Gizligizli

Gizli gizli translates into sneaky sneaky in Turkish. Thank you [twitch](https://www.youtube.com/watch?v=42b6JGSbaAo&t=258s) for being a good naming inspiration :D 

This project aims to hide shellcode inside PE icons using steganography. 



# Introduction

When you run `gizligizli.py`, 

- Given shellcode is embedded into an icon (Can be a custom icon)
- A PE is generated using pyinstaller with malicious icon

When you run the generated exe,

- Program finds the icon and unhides it
- Executes the shellcode


Example icons before and after embedding shellcode,

Original Icon              |  Shellcode Embedded Icon
:-------------------------:|:-------------------------:
![Original Icon](images/default.ico "Original Icon")    |   ![Shellcode Embedded Icon](images/default_embedded.ico "Shellcode Embedded Icon")
![Original Icon](images/test.png "Original Icon")   |   ![Shellcode Embedded Icon](images/test_embedded.png "Shellcode Embedded Icon")




Top left pixel holds the shellcode length. For example, if the shellcode length is 493, top left pixel holds the RGB value (255,238,0). 

Shellcode length many pixels is used and shellcode is embedded into R values. This is possible as each channel can have values between 0x00-0xff.


# Demo


# Example run

```
python3 -m pip install -r requirements.txt
```

```
python3 gizligizli.py
```
