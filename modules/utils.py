import os

def mkdir_p(DIR_NAME):
    """
    Creates a directory and any necessary parent directories. 
    Equivalent to the 'mkdir -p' command in Unix-like systems.

    Args:
        DIR_NAME (str): The directory path to create.
    """
    command = "mkdir -p " + DIR_NAME
    print(command)

    os.system(command)

def rm_r(DIR_NAME):
    """
    Removes a directory and its contents recursively.
    Equivalent to the 'rm -r' command in Unix-like systems.

    Args:
        DIR_NAME (str): The directory path to remove.
    """
    command = "rm -r " + DIR_NAME
    print(command)

    os.system(command)

def cp_r(INPUT_DIR_NAME, OUTPUT_DIR_NAME):
    """
    Copies a directory and its contents recursively to a new location.
    Equivalent to the 'cp -r' command in Unix-like systems.

    Args:
        INPUT_DIR_NAME (str): The source directory path to copy.
        OUTPUT_DIR_NAME (str): The destination directory path.
    """
    command = "cp -r " + INPUT_DIR_NAME + " " + OUTPUT_DIR_NAME
    print(command)

    os.system(command)
    
def str2bool(v):
    """
    Converts a string representation of a boolean value to a boolean type.
    Handles common string values for true/false such as 'yes', 'no', 'true', 'false', etc.

    Args:
        v (str or bool): The string or boolean value to convert.

    Returns:
        bool: The corresponding boolean value.

    Raises:
        argparse.ArgumentTypeError: If the input string does not represent a valid boolean value.
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
