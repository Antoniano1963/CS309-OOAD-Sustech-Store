
def check_args_valid(args_List):
    for arg in  args_List:
        if len(arg) == 0:
            return False
    return True