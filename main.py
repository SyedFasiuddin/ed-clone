import sys
import re
from pathlib import Path

insert_mode_ = False    # default when ed starts
buffer_modified_ = False    # empty buffer is started

file_name_ = ""
lines = [] # empty buffer

prompt_ = ""
prompt_on_ = False
cmd_buf_ = ""

first_addr_ = 0
second_addr_ = 0
last_addr_ = 0

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
        else:
            global file_name_
            file_name_ = argv[1]
    return

def open_file_get_all_content_into_buf():
    global lines
    global last_addr_
    global file_name_

    if file_name_ != "":
        f = Path(file_name_)
        lines = []
        if f.exists():
            print(f.stat().st_size)
            l = f.read_text().split("\n")
            for line in l:
                lines.append(line + "\n")
            lines.pop() # EOF trim
            last_addr_ = len(lines) - 1 if len(lines) > 0 else 0
        else:
            print("No such file or directory")
    return

def write_buf_to_file():
    global buffer_modified_
    global file_name_

    if file_name_ == "":
        print("?")
        return

    # open file to write
    f = Path(file_name_)
    if f.exists():
        fp = f.open("w")
        # clear everything in file
        fp.seek(0)
        fp.truncate()

        # write entire buffer to file
        for line in lines:
            fp.write(line)

        # close file
        fp.close()

    # set buffer back to unmodified
    buffer_modified_ = False
    return

def insert_text_into_buf(mode):
    global buffer_modified_
    global insert_mode_
    global last_addr_

    insert_mode_ = True

    while(insert_mode_):
        line = input()

        if len(line) == 1 and line == ".":
            insert_mode_ = False
            continue

        buffer_modified_ = True
        # lines.append(line + "\n")
        if mode == "i":
            lines.insert(last_addr_, line + "\n")
        elif mode == "a":
            lines.insert(last_addr_ + 1, line + "\n")
        last_addr_ = last_addr_ + 1

    return

def check_addr_range():
    if first_addr_ > second_addr_ or second_addr_ > last_addr_:
        print("?")
        return False
    return True

def print_buffer():
    f = first_addr_ - 1
    s = second_addr_ - 1
    # if check_addr_range():
    #     return
    while(f <= s):
        print(lines[f], end="")
        f = f + 1
    return

def delete_lines():
    global last_addr_
    lines.pop(last_addr_ - 1)
    last_addr_ = last_addr_ - 1
    return

def parse_cmd_buf(buf):
    global first_addr_
    global second_addr_
    global last_addr_
    global prompt_
    global prompt_on_
    global file_name_
    global lines

    # prompt string
    r = re.search(r"P( *)(.*)$", buf)
    if r:
        if r.group(2) == "":
            if prompt_ == "":
                prompt_ = "*"
                prompt_on_ = not prompt_on_
                return "P"
            prompt_on_ = not prompt_on_
            return "P"
        prompt_ = r.group(2)
        prompt_on_ = prompt_on_ if prompt_on_ else not prompt_on_
        return "P"

    # edit this file
    r = re.search(r"e( *)(.*)$", buf)
    if r:
        if r.group(2) == "": # if file is not specified
            print("?")
            return "e"
        file_name_ = r.group(2)
        open_file_get_all_content_into_buf()
        return "e"

    # set file name
    r = re.search(r"f( *)(.*)$", buf)
    if r:
        if r.group(2) == "": # if file is not specified
            if file_name_ == "":
                print("?")
                return "f"
            print(file_name_)
            return "f"
        file_name_ = r.group(2)
        return "f"

    # write to file
    r = re.search(r"w( *)(.*)$", buf)
    if r:
        if r.group(2) == "":
            if file_name_ == "":
                print("?")
                return "w"
            write_buf_to_file()
            return "w"
        file_name_ = r.group(2)
        write_buf_to_file()
        return "w"
    
    r = re.search(r"d", buf)
    if r:
        delete_lines()

    # insert mode with addresses
    r = re.search(r"^([0-9]*)i$", buf)
    if r:
        if r.group(1) == "":
            return "i"
        addr_ = int(r.group(1))
        if addr_ == 0:
            return ""
        last_addr_ = addr_
        return "i"

    # append mode with addresses
    r = re.search(r"^([0-9]*)a$", buf)
    if r:
        if r.group(1) == "":
            return "a"
        addr_ = int(r.group(1))
        if addr_ == 0:
            last_addr_ = -1
            return "a"
        last_addr_ = addr_
        return "a"

    # parse things with two addresses
    r = re.search(r"([0-9].*),([0-9].*)([a-z].*$)", buf)
    if r:
        first_addr_ = int(r.group(1))
        second_addr_ = int(r.group(2))
        return r.group(3)

    # parse things with one address
    r = re.search(r"([0-9].*)([a-z].*$)", buf)
    if r:
        if len(r.group(2)) > 1:
            return ""
        last_addr_ = int(r.group(1))
        return r.group(2)

    # parse without any address
    r = re.search(r"([a-z].*$)", buf)
    if r:
        first_addr_ = second_addr_ = last_addr_
        return r.group(1)

def main_loop():
    open_file_get_all_content_into_buf()
    global cmd_buf_
    global prompt_
    while(True):
        cmd_buf_ = input(prompt_ if prompt_on_ else "")
        c = parse_cmd_buf(cmd_buf_)
        if c == "a":
            insert_text_into_buf(c)
        elif c == "i":
            insert_text_into_buf(c)
        elif c == "d":
            delete_lines()
        elif c == "p":
            print_buffer()
        # elif c == "w" or c == "W":
        #     write_buf_to_file()
        elif c == "q" or c == "Q":
            if not buffer_modified_:
                exit(0)
            confirm_quit = input("Warning: buffer modified\n")
            if confirm_quit == "q":
                exit(0)
            else: cmd_buf_ = confirm_quit
        elif c == "e" or c == "P" or c == "f" or c == "w":
            continue
        else:
            print("?")


if __name__ == "__main__":
    handel_command_line_args(sys.argv)
    main_loop()

