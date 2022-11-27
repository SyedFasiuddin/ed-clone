import sys

def handel_command_line_args(argv):
    if "--version" in argv:
        print("Python clone of ed, the standard UNIX line editor")
        exit(0)
    # for i, arg in enumerate(argv):
    #     print(i, arg)
    return
    
def main(argv):
    handel_command_line_args(argv)

    while(True):
        i = input("")
        if len(i) > 1:
            print("?")
        elif i == "q":
            exit(0)

if __name__ == "__main__":
    main(sys.argv)

