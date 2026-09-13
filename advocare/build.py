# build.py
import subprocess

def main():
    subprocess.run(['python', 'manage.py', 'migrate', '--noinput'])
    print("Migrations applied.")

if __name__ == '__main__':
    main()