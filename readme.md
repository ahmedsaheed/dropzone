## Dropbox Replica using GCP.

To get strated, run the below bash script then open `http://localhost:8000/` on your browser.

```console
bash ./start.sh
```

<details>
<summary>Requirements</summary>

1. **Application login/logout service:**

   - [x] Must match provided examples exactly.
   - [x] Requires `firebase-login.js` and `local-constants.py` setup as shown in examples.

2. **Data Model:**

   - [x] Create collections for `User`, `Directory`, and `File` with appropriate datatypes.
   - [x] Create a default root directory (path of "/") for a user upon first login.

3. **Create Directory:**

   - [x] Implement functionality for users to create directories.

4. **Delete Directory:**

   - [x] Implement functionality for users to delete directories.

5. **Change Directory:**

   - [x] Allow users to change into specific directories.

6. **Navigate Up:**

   - [x] Allow users to navigate up a directory level using a special entry (path of "../").

7. **Root Directory Navigation:**

   - [x] Prevent displaying the ".." entry when a user is in their root directory.

8. **File Upload:**

   - [x] Enable users to upload files to the current directory, storing them in the cloud storage bucket.
   - [x] Prompt for overwrite confirmation if a file with the same name already exists.

9. **Delete File:**

   - [x] Allow users to delete files from the current directory.

10. **Download File:**

    - [x] Implement functionality for users to download files from the current directory to their local machine.

11. **Directory Deletion Protection:**

    - [x] Prevent deletion of directories containing files or subdirectories.

12. **Duplicate File Detection:**

    - [x] Use hashing to identify and highlight duplicate files within the current directory.

13. **Dropbox-wide Duplicate Detection:**

    - [x] Implement functionality to detect duplicate files across a user's entire Dropbox, displaying matching files and their paths.

14. **File Sharing:**

    - [ ] Allow users to share files with read-only access to other user accounts.

15. **UI Design:**
    - [x] Create a well-designed, intuitive, and user-friendly UI.

- [x] Duplicate directory names in the same location.
- [x] Incorrect directory deletion.
- [x] Unconfirmed file overwrites.
- [x] Incorrect file deletion.

</details>
