from dotenv import load_dotenv
import os

load_dotenv()

max_length = int(os.environ["LOGS_MAX_LENGTH"])
save_length = int(os.environ["LOGS_SAVE_LENGTH"])

def write_to_log(log_file, heading, new_line):
    lines = None
    with open(log_file, "r+") as f:
        lines = f.readlines()
        lines = [j.strip() for j in lines if j and j!="\n"]
        if not lines:
            f.write(heading)
        if len(lines) <= max_length:
            lines = None
        elif len(lines) > max_length:
            lines = lines[len(lines) - save_length:]
        f.close()
    if lines:
        with open(log_file, "w") as sf:
            sf.write(heading)
            for l in lines:
                sf.write("\n"+l)
            sf.close()
    with open(log_file, "a") as f:
        f.write(new_line)
        f.close()
