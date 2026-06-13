# Local Request Manager

A small FastAPI web app for local businesses to collect and manage customer requests.

## Problem

Small local businesses often receive customer requests through many different channels, such as phone calls, social media messages, emails, and handwritten notes. This makes it easy to lose requests or forget their status.

## Solution

Local Request Manager provides a simple public request form and an admin page where the business owner can view and manage incoming customer requests.

## Target Users

This app is designed for small local businesses such as:

* car repair shops
* hair salons
* computer repair technicians
* plumbers or electricians
* tutoring centers
* pet grooming businesses

## MVP Features

### Public Side

* Landing page
* Request/contact form
* Success message after form submission

### Admin Side

* View all customer requests
* View request details
* Update request status

## Request Statuses

* new
* in_progress
* completed
* rejected

## Tech Stack

* Python
* FastAPI
* Jinja2 templates
* SQLite
* SQLAlchemy
* HTML
* CSS

## Out of Scope for MVP

The first version will not include:

* React frontend
* Payments
* Email or SMS notifications
* Multi-business SaaS features
* Advanced analytics
* Docker or Kubernetes
* AI features

## Milestones

### Milestone 0: Scope & Setup

Define the project scope, stack, repository name, and README.

### Milestone 1: Basic FastAPI App

Create the initial FastAPI app and render a landing page.

### Milestone 2: Request Form

Create a public request form and handle submissions.

### Milestone 3: Database

Store customer requests in SQLite.

### Milestone 4: Admin Requests List

Display submitted requests in an admin page.

### Milestone 5: Status Management

Allow the admin to update request statuses.

### Milestone 6: Deployment Prep

Polish the README, add screenshots, and prepare for deployment.
