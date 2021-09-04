import os


def testing_callback(filepath, method_id):
    p = (os.path.abspath(filepath) + '/' + method_id).replace('\\', '/')
    with open("results.txt", "a") as f:
        f.write(p + '\n')


def clear_results():
    try:
        os.remove("results.txt")
    except FileNotFoundError:
        pass


def get_results():
    with open("results.txt", "r") as f:
        res = f.read()
    return res.split('\n')[:-1]
