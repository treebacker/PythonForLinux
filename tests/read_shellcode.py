import sys


def read_payload(path):
    with open(path, 'rb') as f:
        content = f.read()
    return content
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(-1)
    
    
    content = read_payload(sys.argv[1])
    print(content)