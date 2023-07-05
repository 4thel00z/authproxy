from sys import argv

from libauthproxy import hash_password

if __name__ == '__main__':
    print(hash_password(argv[1]))
