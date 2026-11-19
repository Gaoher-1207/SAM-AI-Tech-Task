# Final Submission Guide — StudentHub

**Internship:** SAM AI Technologies — 20th August Batch  
**Project:** StudentHub — Student Management System  
**Official deadline:** 20 November 2026

## Official internship requirements

- Complete at least three tasks; additional tasks are optional.
- A LinkedIn video explaining completed tasks is optional.
- If posting on LinkedIn, tag **@SAM AI Technologies** and include **#SAMAITechnologies**.
- Create a GitHub repository with the exact name **SAM AI Tech Task**.
- Upload all completed tasks to that repository.
- Share the GitHub repository link in the official task submission form.
- Submit by **20 November 2026**.

## Project summary

StudentHub is a Flask and SQLite web application for maintaining student records and reviewing academic performance. It includes student CRUD operations, input validation, CSRF protection, case-insensitive unique email addresses, search/filter/sort/pagination, grade calculations, and a responsive dashboard. Setup and local run instructions are in [README.md](README.md).

## Completed internship tasks

1. **Project setup and pages:** Flask application structure, dashboard, About, and Contact pages.
2. **User input:** Student record forms with validation for profile data and marks.
3. **Logic and calculations:** Grade, percentage, average, and pass/fail calculations.
4. **Data storage and management:** SQLite persistence, create/read/update/delete, search, filtering, sorting, and pagination.
5. **Review and presentation:** Responsive interface, security safeguards, automated tests, documentation, and five screenshots.

Evidence and detail: [PROJECT_REPORT.md](PROJECT_REPORT.md), [TESTING_REPORT.md](TESTING_REPORT.md), [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md), and screenshots under `screenshots/`.

## GitHub repository setup

1. Sign in to GitHub and create a **new empty repository** named exactly `SAM AI Tech Task` (the URL slug will be `SAM-AI-Tech-Task`). Do not initialize it with a README, license, or `.gitignore`, because this project already has those files.
2. From this project directory, check the staged file list before committing:

   ```powershell
   git status --short
   git check-ignore students.db .venv .env
   ```

   The local database, virtual environment, secrets, caches, and bytecode are excluded by `.gitignore`. Keep `.env.example`, source, reports, tests, and screenshots.
3. If Git is not initialized yet, initialize and create the local commit:

   ```powershell
   git init
   git branch -M main
   git add .
   git status --short
   git commit -m "Prepare StudentHub internship submission"
   ```

4. Connect the exact repository URL. Replace `<YOUR-GITHUB-USERNAME>` with your account name:

   ```powershell
   git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/SAM-AI-Tech-Task.git
   git remote -v
   ```

   If `origin` already exists, inspect it with `git remote -v`; do not overwrite an existing remote. Only add or change a remote after confirming it is the intended new repository.
5. When ready to upload, push explicitly:

   ```powershell
   git push -u origin main
   ```

   Review the destination and staged/committed content before running the push. The project has not been pushed by this preparation.

## LinkedIn optional video

If you choose to post a video, briefly demonstrate the dashboard, adding/editing a student, searching or filtering, and the grade calculation. Explain the task areas you completed. Tag **@SAM AI Technologies** and include **#SAMAITechnologies**. The video is optional; follow any additional instructions in the official form.

## Google Form submission checklist

- [ ] Confirm the GitHub repository is named exactly **SAM AI Tech Task**.
- [ ] Upload/push the completed project and verify the repository page shows source, tests, documentation, and screenshots.
- [ ] Copy the repository URL from GitHub.
- [ ] Enter that repository link in the official SAM AI Technologies Task Submission Form.
- [ ] Complete any other required fields and submit the form yourself.
- [ ] Optional: publish the LinkedIn video with the required tag and hashtag.
- [ ] Complete submission before **20 November 2026**.

The repository has not been created remotely, the project has not been pushed, and the form has not been submitted as part of this preparation.
