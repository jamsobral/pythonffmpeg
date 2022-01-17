import sys
import os, ffmpeg
from glob import glob

def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)


    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files

def compress_video(video_full_path, output_file_name, target_size):
    # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(video_full_path)
    # Video duration, in s.
    duration = float(probe['format']['duration'])
    # Audio bitrate, in bps.
    has_audio = False
    audio_bitrate = 200
    for s in probe['streams']:
        if s['codec_type'] == 'audio':
            audio_bitrate = s['bit_rate']
            has_audio = True
    #audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])

    # Target total bitrate, in bps.
    for s in probe['streams']:
        if s['codec_type'] == 'video':
            vid_bitrate = int(s['bit_rate'])
            video_bitrate = vid_bitrate * target_size / 100

    i = ffmpeg.input(video_full_path)

    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()

    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()

def print_folders_and_files(subfolders,files):
    print("subfolders")
    for i in subfolders:
        print(i)

    print("files")
    for i in files:
        print(i)

def main():

    input_validation = output_validation = True
    while (input_validation):
        input_folder = input("Enter root input folder: (ex: D:\\OneDrive - dei.uc.pt\\photos&videos\\2021)\n- ")
        if (input_folder == ""):
            input_folder = 'D:\\OneDrive - dei.uc.pt\\photos&videos\\2021'
        if (os.path.isdir(input_folder)):
            input_validation = False
        else:
            print("invalid folder")

    while (output_validation):
        output_folder = input("Enter output folder: (ex: C:\\Users\\JoaoSobral\\Desktop\\outputfolder) \n- ")
        if (output_folder == ""):
            output_folder = "C:\\Users\\JoaoSobral\\Desktop\\outputfolder"
        if (os.path.isdir(output_folder)):
            output_validation = False
        else:
            print("invalid folder")

    #print("From: "+ input_folder + " To: " + output_folder)

    ext = input("File Extension: (default: .mp4 ) \n- ")
    if(not ext):
        ext = ".mp4"

    filesize = input("File Sire reduction in %: (default: 20 ) \n- ")
    if (not filesize):
        filesize = 20

    print("Scanning files inside root input folder")

    subfolders, files = run_fast_scandir(input_folder, [ext])

    print(f"Found files: {len(files)}. Found subfolders: {len(subfolders)}")

    #print_folders_and_files(subfolders,files)
    fails = []
    completed = []
    for file in files:
        try:
            print("compressing " + file)
            str = file[len(input_folder):]
            output_file = f"{output_folder}{str}"
            output_dir = output_file.rsplit('\\', 1)[0]
            try:
                os.makedirs(output_dir)
            except:
                pass
            compress_video(file, output_file, int(filesize))
            completed.append(file)
        except Exception as e:
            fails.append(file)
            print(e)

    print(f"Completed files: {len(completed)}. Fails: {len(fails)}")
    if (len(fails) > 0):
        print("Failed Files:")
        for i in fails:
            print(i)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
