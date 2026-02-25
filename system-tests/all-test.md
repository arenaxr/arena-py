# all-test arena python testing
1. Only test on https://localhost, this uses as self-signed certificate for testing.
1. You will need permission from the user to complete the auth flow once the .sh is started and arena-py attempts its first run.
1. Generate a short/random `scene_id` to be used in the .sh script.
1. Open a web browser to the Arena scene (e.g. https://localhost/`username`/`scene_id`?noname=1&skipav=1&noav=1&demoMode=1&auth=anonymous) and open the browser console to monitor for errors.
1. Run this script with your `scene_id`: `bash system-tests/all-test.sh <scene_id>`
1. Check the log file `system-tests/all-test.log` for any errors or issues that occurred during the execution of the tests.
1. Propose fixes for the errors encountered in the browser console and/or .sh .log output.
