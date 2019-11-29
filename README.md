# KooCook! - Django backend

##### Build status
- `master`: [![CircleCI](https://circleci.com/gh/KooCook/koocook-dj/tree/master.svg?style=shield&circle-token=fd2434f2ab70aacb8216f2242e272abeae57859c)](https://circleci.com/gh/KooCook/koocook-dj/tree/master)  
- `dev`: [![CircleCI](https://circleci.com/gh/KooCook/koocook-dj/tree/dev.svg?style=shield&circle-token=fd2434f2ab70aacb8216f2242e272abeae57859c)](https://circleci.com/gh/KooCook/koocook-dj/tree/dev) [![codecov](https://codecov.io/gh/KooCook/koocook-dj/branch/dev/graph/badge.svg)](https://codecov.io/gh/KooCook/koocook-dj/branch/dev) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/9f6390cd75d94a21a2c4accf997214bf)](https://www.codacy.com/manual/KooCook/koocook-dj?branch=dev&amp;utm_source=github.com&amp;utm_medium=referral&amp;utm_content=KooCook/koocook-dj&amp;utm_campaign=Badge_Grade)
## Description

__KooCook!__ is a web application that helps people—whether they are amateur cooks, homecooks, aspiring cooks, experienced cooks, or just starving people—decide on what food they want to make with the ingredients, equipment, time, and preferences that they have and live a healthier life with nutrition information included.

**This repo** is considered a submodule for the [main app](https://github.com/KooCook/koocook/tree/dev) and act as a backend (backbone) of the project.

## Team Members

| Name (Nickname)   | GitHub ID |
|-------------------|-----------|
| Mai (Mai)         | [MaiMee1](https://github.com/MaiMee1/) \| [MaiNorapong](https://github.com/MaiNorapong/)
| Tharathorn (Mos)  | [th-bunratta](https://github.com/th-bunratta/)
| Chayathon (Plume) | [plumest](https://github.com/plumest/)

## Local Quickstart (Running the app locally)

### Dependency requirements
|Name|Required version(s) |
|:---:|:---:|
|Python | 3.7.3 or higher|
|Django | 2.1 or higher|
|PostgreSQL| 12 or higher|

All other dependencies are specified in `requirements.txt`

### Steps

> Proxy installing via virtualenv is highly recommended
>
> Please consult [this link](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) to learn how to setup *Python virtualenv*

1. Make sure you are in the root directory (repository root) of the project and already clone this repo.
2. Create ```.env``` for your local app environment settings *(Pending guide...)*
    - Make sure your secret key is strong enough. (Recommended: ```PBKDF2``` algorithm with a ```SHA256``` hash)
3. Run <code>pip install -r [requirements.txt](requirements.txt)</code> first to install required packages for the project.
4. _Pending mock data import instructions_
5. If you first set up a repo of the application  on a clean slate, migrate the database as well by running the following Django command: <pre>python [manage.py](manage.py) migrate</pre>
6. Run <pre>python [manage.py](manage.py) runserver</pre> and, Voila!, the server should listen on the default port at <code>localhost:*default_port*</code>.

## Project Documents

- [Iteration Plans (Google Docs)](https://docs.google.com/document/d/1XLrRgLp4s63g2Ep8B8P56WfhL46VF5VlfczcGRQC7_Y/edit)
- [Task board (Trello)](https://trello.com/b/32svKah9/isp19-koocook)
- [Code Review Script and Checklist (Google Docs)](https://docs.google.com/document/d/1GSI0FGx4NZyqwAVUOYt641X0tsdqfeRz3O-R3XnfGFE/edit)
- [Project Proposal (Google Docs)](https://docs.google.com/document/d/1syrJeChO_DoCd_EE_ohzHcz8JPxZUc51QRxZaqScpJ4/edit)
- Static mockup
  - Screenshots & Demo: [Google Drive](https://drive.google.com/drive/folders/1oRqvuTPX0Nw1hI52laHMkh5T0WVMhhqI)
  - Source code: [GitHub](https://github.com/KooCook/koocook-static-mockup)

## Other Links

- **Deployed app:**
    - (Production) https://koocook.appspot.com/ (*Inactive*)
    - (**Development**) https://koocook-deploy.appspot.com/ (**Active**, based on **dev** branch)
- [Project folder (Drive)](https://drive.google.com/open?id=1GpXj0oaM3n29aJF2YNDhjJwkCqqHa-04)
  - This includes mockup screenshots and demo as well.
- [Main app (GitHub)](https://github.com/KooCook/koocook/tree/dev)
- [Django backend (GitHub)](https://github.com/KooCook/koocook-dj/tree/dev)
- [datatrans (GitHub)](https://github.com/KooCook/datatrans) -- supporting package for data transformation

## Notes

### About branching

Our team decided to change from using GitHub Flow to Git Flow, so our main branch is `dev` (mainly for development) and not `master` (production-only)
