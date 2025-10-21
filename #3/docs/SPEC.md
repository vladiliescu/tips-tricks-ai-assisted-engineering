## 1. Project Setup & High-Level Goals

- Goal: Build a predictive analytics application that uses fast GitHub data and team parameters to estimate effort (time/complexity) for future tasks/features.

- Core Features:
  1. Connect to GitHub repositories.
  2. Extract historical data (issues, pull requests, commits).
  3. Combine with team parameters (team size, seniority, technology experience).
  4. Train a prediction model to forecast effort for new tasks/features.
  5. Provide a dashboard/API for estimates.


## 2. Data Sources & Collection

### 2.1 GitHub Integration

- Use GitHub API for:
  - Issues & their metadata (labels, assignees, created/closed dates).
  - Pull requests & commits linked to those issues.
  - Time to close (duration).
- Authentication: Use OAuth2 or GitHub App tokens.


### 2.2 Team Metadata

- A team will have the following associated metadata:
  - Team members.
  - Seniority levels (junior/mid/senior).
  - Technologies and experience level (per team member). - optional TBD
  - Team size per sprint/period.


### 2.3 Manual Input

- Allow manual labeling or tagging of completed tasks with:
  - Actual time spent (if not tracked automatically).
  - Initial estimation (story points or hours).
  - Observations (eg: new technologies, some investigation or design needed)


## 3. Data Processing

- Data Cleaning (examples: normalize issue data, handle missing values for estimation or time spent)
- Feature Engineering (examples: calculate metrics, extract text features, encode team parameters)
- Build a structured dataset combining various features (examples: title, description, tags, complexity, historical time spent vs. estimated, team composition at the time)

## 4. Model Development

- Model Goals: Predict future estimates (time/SP).
- Candidate Algorithms:
  - Regression models
  - NLP-enhanced models using embeddings (for textual task descriptions)??
  - Optionally: Fine-tune a small transformer model (e.g., BERT) on text + numeric features.


## 5. Application Architecture

### 5.1 Backend

- Responsibilities:
  - Fetch data from GitHub.
  - Store data in a database.
  - Run prediction models.
  - Provide REST/GraphQL endpoints.

### 5.2 Database

- Use SQLite

### 5.3 Frontend

- Web app (SvelteKit).
- Features:
  - Dashboard for insights (velocity, accuracy of past estimates).
  - Input form for new tasks/features to predict effort.
  - Display predicted estimates.


## 6. Prediction Workflow

- A new task/feature is created (via manual input or GitHub webhook).
- The system:
  - Collects relevant historical data.
  - Identifies team parameters for that sprint/team.
  - Runs the prediction model.
- Outputs:
  - Predicted story points or hours.
  - Confidence interval.


## 7. Automation & Continuous Improvement

- Webhooks: Set up GitHub webhooks to update data in real-time.
- Model Retraining: Schedule periodic retraining (e.g., weekly).
- Versioning: Keep model versions to track improvement.

## 8. Security & Access

- Secure authentication (OAuth2, JWT).
- RBAC (Role-Based Access Control) for teams.

## 9. Scalability & Deployment - Next phase

- Deploy backend with Docker/Kubernetes.
- Use cloud services (AWS/GCP/Azure).
- CI/CD pipeline for automated deployment.
