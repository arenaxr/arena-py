#!/usr/bin/env python3

from arena import Scene

def main():
    scene = Scene()
    print(f"ARENA Username: {scene.username}")
    print(f"ARENA Token: {scene.remote_auth_token['token']}")

if __name__ == "__main__":
    main()
