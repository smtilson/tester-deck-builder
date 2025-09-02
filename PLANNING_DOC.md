# How to Use This Document (For GitHub Copilot)

This document is the **planning and requirements guide** for the Tester Deck Builder project.  
Whenever you (GitHub Copilot) are given this document as context, you should:

- Treat it as the authoritative source for project goals, requirements, and priorities.
- Follow any guidelines or instructions marked as **Copilot Instructions**.
- Use the answers and clarifications provided to inform your suggestions, code generation, and planning.
- When you see a section or line prefixed with `> Copilot:` or surrounded by `<!-- Copilot Instruction --> ... <!-- End Copilot Instruction -->`, treat it as a direct instruction for your behavior, output, or interpretation.

## Syntax for Copilot Instructions

- Use `> Copilot:` at the start of a line for a brief instruction.
- For longer or multi-line instructions, use HTML comments:
  ```
  <!-- Copilot Instruction -->
  [Your instruction here]
  <!-- End Copilot Instruction -->
  ```

## Guidelines

> Copilot: When generating code, prefer extensibility, clarity, and best practices.
> Copilot: Do not remove comments.
> Copilot: Add comments or docstrings.
> Copilot: Use type hints.
> Copilot: If you notice a missing feature or method, add it with a not implemented exception or commented out.
> Copilot: I have marked groups of tests with the `@pytest.mark.skip` decorator passing it different strings. This is for ease of development, do not remove these even if they are commented out.


<!-- Copilot Instruction -->
Always ask for clarification if requirements are ambiguous or missing.
<!-- End Copilot Instruction -->

---

# Idea
Develop a web app that can be used to build decks for games during playtesting. It should have accounts for developers, staff, designers, as well as playtesters with different levels of permissions and for various different games. I want to develop it in different epochs etc. There will be a fastapi backend and a frontend with vue, angular, or svelte. I am currently undecided, so the parts on developing the front end should/can be slightly vague.

---

# Project Planning Document: Tester Deck Builder

## High-Level Overview

The goal is to develop a web application for building and managing game decks during playtesting. The app will support multiple user roles (developers, staff, designers, playtesters) with different permissions and support multiple games. The backend will be built with FastAPI, and the frontend will use a modern JS framework (Vue, Angular, or Svelte). The project will be developed in iterative "epochs" (agile sprints), with clear milestones and priorities.

---

## Agile Planning & Task Breakdown

### 1. **Project Setup & Initial Planning**
- [ ] Define project goals and success criteria

    #### Success Criteria: Questions to Define Project Success

    To help determine clear success criteria for the project, consider the following questions:

    - What are the primary problems this app should solve for its users?
    Answer: Allow staff to add new versions of cards. Allow playtesters to make decks with cards and still have the historical artifact when new versions are pushed. Eventually, maybe it could help organize the development process.
    - Who are the main user groups, and what are their most important needs? There is staff that need to be able to store different versions of cards throughout the development process. There are playtesters who need to be able to save decks. Also, there is the potential for storing feedback on individual cards as well.
    - What are the minimum features required for the app to be useful to playtesters, designers, and developers?
    Individual accounts with different permissions. Staff (designers and developers) can make new versions of cards available to specific users only (based on which games they are playtesting). Playtesters can create, store, edit, share (and potentially discuss) decks (and maybe cards). The playtesters can look at previous versions of decks with cards that are no longer in the current version of the cardpool.
    - What workflows must be supported for deck building, playtesting, and feedback collection?
    Let's not worry about workflow for playtesting or feedback yet.
    
    Staff should be able to create a game, cards, and push versions to the pool of playtesters so that the current version is available for deckbuilding. Once the version is updated, playtesters should no longer be able to add those cards to a deck.

    Playtesters should be able to create decks, add and remove cards, have the validity of the deck checked (specific to each game). They should also be able to link people to the decks.
    - What performance or reliability standards should the app meet (e.g., uptime, response time)?
    The priority should be on not losing information. I expect there to be a quite small user base.
    - What security/privacy requirements must be met (e.g., user data protection, authentication)?
    Users will need to have permissions set by an admin/staff person who is running the playtest. They should have to log in before using any feature of the site or viewing any card data. The material on the site will be protected by an NDA.
    - What integrations (if any) are required with other tools or platforms?
    I would like integration with google sheets, some image storage, export to a tabletop simulator mod. This is not necessary in the beginning. Perhaps integration with google forms or something of that nature. Maybe discord?
    - What are the measurable outcomes that will indicate the project is successful (e.g., number of active users, feedback collected, decks created)?
    The main measure is functionality, does it work as intended? Is it extensible so that I can add features that users ask for? Is the playtest team happy with it?
    - What is the timeline for delivering the MVP and subsequent releases?
    I don't really know. This is a hobby project that I might potentially try to sell/market.
    - How will user feedback be gathered and incorporated into future development?
    I had thought privately. But perhaps there could be a suggestion box.
    - What are the criteria for considering a feature or sprint “done” (e.g., tested, documented, deployed)?
    A feature should be tested, documented, and deployed.

    > Please answer these questions to help clarify and document the success criteria for your project.

- [ ] Set up repository and initial folder structure

    #### Repository & File Structure: Questions and Tips

    To help set up an effective repository and file structure, consider the following:

    - What are the main components of the project (backend, frontend, tests, docs, scripts)?
    - Should the backend and frontend live in the same repository or be split?
    - How will you organize your API endpoints, models, schemas, and services?
    - Where will you place configuration files (e.g., `.env`, `Dockerfile`, `pyproject.toml`)?
    - How will you structure your test suite (unit, integration, e2e)?
    - What naming conventions will you use for files and folders?
    - How will you handle static assets (images, exports, etc.)?
    - Where will you keep documentation and onboarding guides?
    - Will you use a monorepo structure or keep things modular?
    - How will you organize scripts for data import/export, migrations, etc.?

    ##### Tips & Best Practices

    - Keep related code together (e.g., models, schemas, services for a feature in one folder).
    - Use clear, consistent naming for files and folders.
    - Separate production code from test code.
    - Store configuration and secrets outside of source control (use `.env` and `.gitignore`).
    - Include a `README.md` at the root and in major subfolders.
    - Use a `docker-compose.yml` if you need to orchestrate multiple services.
    - Document your folder structure in the main `README.md`.
    - Regularly review and refactor your structure as the project grows.

    > Please answer these questions and consider these tips to help clarify and document your repository and file structure.

- [ ] Establish coding standards and contribution guidelines

    #### Coding Standards & Contribution Guidelines: Questions and Tips

    To help establish clear coding standards and contribution guidelines, consider the following:

    - What style guide will you follow for Python (PEP8, Black, isort, etc.)?
    - What style guide will you follow for frontend code (ESLint, Prettier, etc.)?
    - Will you use type hints and docstrings throughout the codebase?
    - How will you document functions, classes, and modules?
    - What is your process for code reviews and pull requests?
    - How will you handle branching and merging (e.g., GitFlow, trunk-based)?
    - What are the requirements for test coverage before merging?
    - How will contributors be onboarded and informed of guidelines?
    - Will you use pre-commit hooks or automated linters/formatters?

    ##### Tips & Best Practices

    - Automate formatting and linting with tools like Black, isort, ESLint, and Prettier.
    - Require code reviews for all pull requests.
    - Document your standards in a `CONTRIBUTING.md` file.
    - Use pre-commit hooks to enforce standards before code is pushed.
    - Encourage descriptive commit messages and pull request summaries.
    - Maintain a changelog for major updates.

    > Please answer these questions and consider these tips to help clarify and document your coding standards and contribution guidelines.

- [ ] Choose frontend framework (Vue, Angular, Svelte)

    #### Frontend Framework Selection: Questions and Tips

    To help choose the best frontend framework for your project, consider the following:

    - What is your team's experience with Vue, Angular, or Svelte?
    - What are the strengths and weaknesses of each framework for your use case?
    - How important is performance, scalability, and ecosystem support?
    - Will you need SSR (server-side rendering) or static site generation?
    - Are there existing UI libraries or components you want to use?
    - How easy is it to integrate with your FastAPI backend?
    - What is the learning curve for new contributors?
    - How will you structure your frontend codebase?

    ##### Tips & Best Practices

    - Prototype a simple page in each framework to compare developer experience.
    - Consider long-term maintainability and community support.
    - Document your decision and reasoning for future reference.
    - Plan for integration with authentication and backend APIs.

    > Please answer these questions and consider these tips to help clarify and document your frontend framework selection.

- [ ] Set up CI/CD and testing infrastructure

    #### CI/CD & Testing Infrastructure: Questions and Tips

    To help set up effective CI/CD and testing infrastructure, consider the following:

    - What CI/CD platform will you use (GitHub Actions, GitLab CI, Travis, etc.)?
    - What environments will you deploy to (staging, production)?
    - How will you automate running tests and linters on every push/PR?
    - Will you use Docker for builds and deployments?
    - How will you manage secrets and environment variables in CI/CD?
    - What is your rollback strategy for failed deployments?
    - How will you monitor build status and test coverage?
    - Will you automate deployment to cloud hosting?
    - How will you handle database migrations in CI/CD?

    ##### Tips & Best Practices

    - Start with a simple workflow that runs tests and linters on every push.
    - Use environment-specific configuration files.
    - Automate deployment to staging before production.
    - Integrate code coverage and test reports into your CI dashboard.
    - Document your CI/CD setup in the repository.

    > Please answer these questions and consider these tips to help clarify and document your CI/CD and testing infrastructure.

### 2. **Core Backend Features (FastAPI)**

- [ ] User authentication & authorization
    - [ ] Design user model and roles (developer, staff, designer, playtester)
    - [ ] Implement registration endpoint
        - [ ] Validate required fields
        - [ ] Handle duplicate email/username
        - [ ] Send verification email (if needed)
    - [ ] Implement login endpoint
        - [ ] Validate credentials
        - [ ] Return JWT tokens
        - [ ] Handle inactive/unverified users
    - [ ] Implement password reset
        - [ ] Forgot password endpoint (request token)
        - [ ] Reset password endpoint (validate token, update password)
        - [ ] Enforce password policy and matching confirmation
    - [ ] Implement role management
        - [ ] Assign roles to users
        - [ ] Restrict access to endpoints based on role
        - [ ] Admin/staff role assignment interface

- [ ] Deck management
    - [ ] Design deck and card models
    - [ ] Implement CRUD endpoints for decks
        - [ ] Create deck
        - [ ] Read/list decks (with filters)
        - [ ] Update deck (name, description, etc.)
        - [ ] Delete deck
    - [ ] Implement CRUD endpoints for cards
        - [ ] Create card (with versioning)
        - [ ] Read/list cards (with filters)
        - [ ] Update card (new version, metadata)
        - [ ] Delete card
    - [ ] Assign cards to decks
        - [ ] Add card to deck
        - [ ] Remove card from deck
        - [ ] Validate deck legality (game-specific rules)
    - [ ] Support for multiple games
        - [ ] Game model and CRUD endpoints
        - [ ] Associate decks and cards with games
        - [ ] Filter decks/cards by game

- [ ] Playtesting features
    - [ ] Assign playtesters to games/decks
        - [ ] Endpoint to assign playtesters
        - [ ] Restrict deck/card access based on assignment
    - [ ] Collect feedback
        - [ ] Feedback model (comments, ratings, bug reports)
        - [ ] Endpoint to submit feedback on decks/cards
        - [ ] Endpoint to view feedback (by staff/designers)
    - [ ] Track playtesting sessions

### 3. **Frontend Features**
- [ ] Basic UI scaffolding
- [ ] Authentication screens
- [ ] Deck and card management interfaces
- [ ] Playtesting dashboard
- [ ] Responsive design

### 4. **Testing & Quality Assurance**
- [ ] Unit tests for backend
- [ ] Integration tests for backend
- [ ] End-to-end tests for frontend
- [ ] Manual QA checklist

### 5. **Deployment & Operations**
- [ ] Dockerize backend and frontend
- [ ] Set up cloud hosting (Heroku, AWS, etc.)
- [ ] Monitor errors and performance (Sentry, logging)
- [ ] Documentation for deployment and onboarding

---

