# Centralized User Badges application
Application responds to users in the scene and updates the user avatar with name and badge updates.

Uses a central file, the local example can be used but should be modified with real ARENA account usernames and hosted at location you control.

Test locally:
```bash
cd tools/badges
python -m http.server &
python3 tools/badges/badges.py -u http://localhost:8000/users.csv
```

Expects CSV first row headers of:
```
Username,Name,Role,Email,Phone Number,Address
```
