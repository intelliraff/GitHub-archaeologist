# GitHub Archaeologist — Version 0.1

## Overview

GitHub Archaeologist is a Flask-based repository analysis platform that helps developers evaluate the health and activity of GitHub repositories.

The application allows users to create accounts, authenticate securely, analyze repositories, and maintain a history of previous analyses.

---

## Features Implemented

### Authentication System

* User registration
* User login
* Password hashing using Werkzeug
* Session-based authentication
* JWT token generation
* Automatic logout on token expiration

### Repository Analysis

Users can submit any public GitHub repository URL.

The application fetches repository metadata using the GitHub REST API and analyzes:

* Repository owner
* Repository name
* Stars
* Forks
* Open issues
* Primary language
* Last updated date

### Activity Detection

Repositories are classified into:

* Active 🌱
* Slow 🚸
* Abandoned 🆘

based on recent activity.

### Contributor Analysis

The application calculates:

* Number of contributors
* Individual contribution counts
* Contribution percentages

### Health Score System

A repository health score is generated using:

* Repository activity
* Contributor count
* Open issue count

Health score is reported on a scale of 0–100.

### User History Tracking

Every repository analysis performed by a user is stored.

Stored information includes:

* Repository name
* Owner
* Health score
* Activity status
* Timestamp

Users can retrieve their analysis history through the history endpoint.

### Database Models

#### User

Stores:

* Username
* Hashed password

#### Repository

Stores:

* Repository metadata
* Statistics
* Last update information

#### Analysis

Stores:

* Repository analysis results
* User ownership
* Health score
* Activity status

---

## Technology Stack

Backend:

* Flask
* SQLAlchemy
* SQLite

Authentication:

* JWT
* Flask Sessions
* Werkzeug Security (hashing the password!)

External APIs:

* GitHub REST API (ofcourse, the project is on github, so we use github apis!)

---

## Current Limitations

* No frontend dashboard visualizations
* No GitHub OAuth integration
* Basic health score algorithm
* No commit trend analysis
* No pull request analysis
* No NLP capabilities yet

---

## Planned Features (Version 0.2)

### Repository Archaeology

* Commit analysis
* Commit frequency tracking
* Repository timeline generation
* Dead repository detection
* Advanced health scoring

### Contributor Insights

* Top contributor ranking
* Contribution trend visualization
* Contributor activity tracking

### NLP Features

* README summarization
* Repository description generation
* Issue categorization
* Project topic extraction

### UI Improvements

* Interactive dashboard
* Charts and graphs
* User profile page
* Analysis history page

---

## Status

Version: 0.1

Development Stage: Early Prototype

Author: Akhila Sai👩🏻‍💻

Goal: Build an intelligent GitHub repository analysis platform combining software engineering analytics and NLP.

PS: I mostly hardcoded the whole thing. Used chatgpt as a mentor: what to do, in what order, and making it correct my mistakes! 😌