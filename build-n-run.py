#!/usr/local/bin/python3
import os, errno
import shutil
import glob
import subprocess


''' 
What we want to do is:
 1. go into each directory 
 2. make a "Linux" directory
 3. cat the *.playground/Contents.swift files to Linux/main.swift
 4. check for any additional *.swift files and copy them to Linux
 5. build an executable
 6. if the executable built, try to run it
'''
good_list = list()
bad_list = list()


def findAndCopy(src, dest):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        # Ignore the linux directory we just created
        if os.path.isdir(s) and s.endswith("linux") != True:
            findAndCopy(s, dest)
        # only want swift files
        elif s.endswith(".swift"):            
            try:
                # We need to explicitly check for Contents.swift, which
                # is the main playground file, and for compiling, we need
                # to rename it to "main.swift"
                if s.endswith("Contents.swift"):
                    shutil.copy(s, os.path.join(dest, "main.swift"))   
                else:
                    shutil.copy(s, dest)
            except shutil.SameFileError:
                pass
   

def build(dir):
    print("We're now in", dir)
    os.chdir(dir)
    # Grab all the swift files
    files = glob.glob("*.swift")
    # Build the actual command we're going to run
    cc = "swiftc " + " ".join(files)    
    print(cc)

    # And compile it    
    process = subprocess.Popen(cc, shell=True, stdout=subprocess.PIPE)
    process.wait()
    if process.returncode == 0:
        # Cool, it compiled
        print("Yay, we got an executable")
        good_list.append(dir)
        main_process = subprocess.Popen("./main", shell=True, stdout=subprocess.PIPE)
        main_process.wait()
        if main_process.returncode == 0:
            print("We ran it!")            
        else:
            print("Hmm, there was an error running the process")
    else:
        print("Program didn't build correctly")
        bad_list.append(dir)
    

def buildAndTest(d):
    print("---> Now working with", d)    
    # Change to the subdirectory
    os.chdir("./" + d)

    # If the linux directory exists, delete it
    # so we can start fresh
    if os.path.exists("linux"):
        shutil.rmtree('linux')

    # Now we'll make the "Linux" directory    
    try:
        os.makedirs("linux", exist_ok = False)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise    

    # Now we gather all the swift files into the linux
    # directory
    findAndCopy(".", os.path.abspath(os.curdir + "/linux"))
    
    # Now let's build and run the files
    build(os.path.abspath(os.curdir + "/linux"))

    # And make sure we're back in the current directory
    os.chdir("..")

    # And return back up to the top
    os.chdir("..")


'''
B E G I N
'''
algos = next(os.walk('.'))[1]
algo_iter = iter(algos)
for alg in algo_iter: 
    # Skip any of the hidden directories (e.g. .git)
    if alg[0] == '.':
        continue
    buildAndTest(alg)

# Now go through the lists
print("=== G O O D  L I S T ===")
for i in range(len(good_list)):
    print(good_list[i])

print("=== B A D  L I S T ===")
for i in range(len(bad_list)):
    print(bad_list[i])
