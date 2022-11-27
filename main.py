import sys

insert_mode_ = False    # default when ed starts
buffer_modified_ = False    # empty buffer is started

lines = [] # empty buffer

def handel_command_line_args(argv):
    if len(argv) > 1:
        if "--version" == argv[1]:
            print("vbeta.0.1.0")
            print("Python clone of ed, the standard UNIX line editor")
            exit(0)
        elif "--help" == argv[1]:
            print("Usage:\n" +
                  "  ed                    Start with empty buffer\n" +
                  "  ed [file]             Edit file\n" +
                  "  ed [options] [file]   \n" +
                  "\n" +
                  "Options:\n" +
                  "  -v\n" +
                  "  -p"
                 )
            exit(0)
        elif "-" in argv[1]:
            print(f"ed: invalid option -- '{argv[1]}'\n" +
                  "Try 'ed --help' for more information."
                 )
            exit(1)

def insert_mode():
    insert_mode_ = True

    while(insert_mode_):
        line = input()

        if len(line) == 1 and line == ".":
            insert_mode_ = False
            continue

        global buffer_modified_
        buffer_modified_ = True
        lines.append(line)

    return

def print_buffer():
    for line in lines:
        print(line)
    return
    
def main_loop():
    while(True):
        i = input("")
        if len(i) > 1:
            print("?")
        elif i == "i":
            insert_mode()
        elif i == "p":
            print_buffer()
        elif i == "q":
            if not buffer_modified_:
                exit(0)
            confirm_quit = input("Warning: buffer modified\n")
            if confirm_quit == "q":
                exit(0)
            else: i = confirm_quit
        else:
            print("?")


if __name__ == "__main__":
    handel_command_line_args(sys.argv)
    main_loop()

