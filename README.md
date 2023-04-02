<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Apache 2.0 License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <!-- <a href="https://github.com/capcom6/bitbucket-issues">
    <img src="assets/logo.svg" alt="Logo" width="80" height="80">
  </a> -->

  <h3 align="center">BitBucket Issues Dashboard</h3>

  <p align="center">
    The application provides a centralized dashboard for viewing issues list from multiple repositories in a single place.
    <br />
    <!-- <a href="https://github.com/capcom6/bitbucket-issues"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/capcom6/bitbucket-issues">View Demo</a> -->
    ·
    <a href="https://github.com/capcom6/bitbucket-issues/issues">Report Bug</a>
    ·
    <a href="https://github.com/capcom6/bitbucket-issues/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
- [About The Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [How it works](#how-it-works)
  - [Configuration](#configuration)
  - [Security](#security)
  - [Release notes](#release-notes)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://github.com/capcom6/bitbucket-issues)

The project was created in response to a common problem faced by teams using BitBucket to manage their code repositories: how to keep track of issues across multiple repositories.

Until recently, there was a centralized dashboard page at https://bitbucket.org/dashboard/issues, which provided a consolidated view of all issues assigned to the user. This dashboard page was a valuable tool for users, as it allowed them to quickly catch up on old issues, prioritize tasks, and ensure that nothing fell through the cracks. However, the dashboard page was phased out.

Recognizing the need for a centralized and user-friendly solution to manage issues across multiple repositories in BitBucket, this project was created.

The application provides an easy-to-use interface for viewing issues in a BitBucket workspace from multiple repositories in one place, making it easier for teams to collaborate and stay organized. This is especially useful for teams that work on multiple projects or use multiple repositories to manage their code.

In addition to providing a consolidated view of issues, the application allows users to filter issues across multiple repositories based on specific criteria, such as issue type, priority, and assignee. This can save time and effort, as users do not need to manually search through each repository to find relevant issues.

The project is in the MVP stage.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python]][Python-url]
* [![Redis][Redis]][Redis-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Follow the instructions below to run local copy of service with Docker.

### Prerequisites

To run the app with Docker, you will need to have Docker installed on your system and have a basic understanding of Docker containers and how to manage them using Docker Compose or other tools.

### Installation

1. Create an application password for your BitBucket account, if you haven't already done so. You can do this by going to your BitBucket account settings and selecting "App passwords" from the sidebar. Follow the prompts to create a new application password with the necessary permissions for accessing your repositories and issues.
2. Copy the default [config.example.yml](./configs/config.example.yml) file located in the configs folder, and rename it to `config.yml`. Update the values in the config.yml file with your BitBucket username, password, and other settings as needed. Alternatively, you can create a new `config.yml` file from scratch, using the format described in the [Configuration](#configuration) section.
3. Run the Docker container with the `capcom6/bitbucket-issues` image, and expose port 8000 to access the web interface. You can do this by running the following command: `docker run -d -p 8000:8000 -v $(pwd)/config.yml:/app/config.yml capcom6/bitbucket-issues:latest`

This command will start the Docker container and mount your custom `config.yml` file as a volume in the container. The container will listen on port 8000, which you can access in your web browser by navigating to http://localhost:8000 or http://&lt;docker-machine-ip&gt;:8000, depending on your Docker setup.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

### How it works

Here's an overview of how the application works:

1. The application reads the configuration settings from the `config.yml` file, which specifies the BitBucket access settings, issue loading settings, and cache storage settings.
2. The application connects to the BitBucket Cloud API using the specified login and app password, and loads issues from the specified repositories and filters.
3. The application caches the loaded issues in memory or Redis, depending on the specified cache storage settings and the TTL (Time-To-Live) value.
4. The application starts a web server and serves a user interface that allows users to view the loaded issues. Users can filter and sort issues based on various criteria, such as issue type, priority, and assignee.
5. When a user selects an issue, the application provides a direct link to the issue in BitBucket, allowing the user to view and modify the issue as needed.
6. The application automatically refreshes the cached issues based on the TTL value specified in the `config.yml` file. This ensures that the cached issues are up-to-date and accurate, without overloading the BitBucket API with frequent requests.

### Configuration

The application is configured using the `config.yml` file, which specifies the BitBucket access settings, issue loading settings, and cache storage settings. However, it is also possible to provide these configuration values using environment variables like `BITBUCKET__LOGIN` with double underscores between parent-child sections.

```yaml
bitbucket: # BitBucket access settings
  login: login # User login for the BitBucket account.
  password: password # App password for the BitBucket account, with read access to account info, repositories, and issues.
  owner: owner # The owner of the repositories to load issues from.

issues: # Issues loading settings
  repositoriesFilter: # A filter for the repositories to load issues from, using BitBucket's JQL syntax.
  issuesFilter: (state = "new" OR state = "open" OR state = "on hold") AND (priority = "major" OR priority = "critical" OR priority = "blocker") # A filter for the issues to load, using BitBucket's JQL syntax.

storage: # Cache storage settings
  dsn: memory:// # The DSN (Data Source Name) for the cache storage. Supports memory:// and redis:// schemes.
  ttl: PT6H # The TTL (Time-To-Live) for cached items, specified in ISO 8601 duration format.
```

### Security

The application does not include any built-in authorization or authentication mechanism. To enhance security, it is recommended to use an external service or tool, such as Nginx, to provide basic authentication and restrict access to the application. Alternatively, deploying the application in a private network can provide an additional layer of security and help prevent unauthorized access from external sources.

### Release notes

* When you first launch the application, it may take some time to load issues from BitBucket, depending on the number of repositories and issues. During this loading period, the UI may display 0 issues. Please be patient and allow the application time to load the issues. Subsequent loads should be faster, as issues are cached for improved performance.
* The user interface of the application, as well as some parts of the documentation, were created by ChatGPT, a large language model trained by OpenAI. While ChatGPT's responses are typically accurate and informative, please note that they are generated by a machine learning model and may not always be perfect.

<!-- _For more examples, please refer to the [Documentation](https://example.com)_ -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/capcom6/bitbucket-issues/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the Apache-2.0 license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Project Link: [https://github.com/capcom6/bitbucket-issues](https://github.com/capcom6/bitbucket-issues)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* The BitBucket development team, for creating and maintaining a powerful and flexible platform for managing code repositories, and for providing a comprehensive and well-documented API.
* Redis Labs, for providing a powerful and scalable in-memory database solution, which is used to cache issues and improve performance.
* The developers of the "bitbucket-python" library (https://github.com/GearPlug/bitbucket-python), which provides a convenient and easy-to-use interface for accessing the BitBucket API from Python.
* The "FastAPI" web framework (https://fastapi.tiangolo.com/), which is used to build the backend API.
* OpenAI, for developing and providing access to ChatGPT, a large language model used to generate some of the UI and documentation content.

<!-- Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)-->

<p align="right">(<a href="#readme-top">back to top</a>)</p> 



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/capcom6/bitbucket-issues.svg?style=for-the-badge
[contributors-url]: https://github.com/capcom6/bitbucket-issues/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/capcom6/bitbucket-issues.svg?style=for-the-badge
[forks-url]: https://github.com/capcom6/bitbucket-issues/network/members
[stars-shield]: https://img.shields.io/github/stars/capcom6/bitbucket-issues.svg?style=for-the-badge
[stars-url]: https://github.com/capcom6/bitbucket-issues/stargazers
[issues-shield]: https://img.shields.io/github/issues/capcom6/bitbucket-issues.svg?style=for-the-badge
[issues-url]: https://github.com/capcom6/bitbucket-issues/issues
[license-shield]: https://img.shields.io/github/license/capcom6/bitbucket-issues.svg?style=for-the-badge
[license-url]: https://github.com/capcom6/bitbucket-issues/blob/master/LICENSE.txt
[product-screenshot]: https://github.com/capcom6/bitbucket-issues/raw/master/assets/ui.png
[Python]: https://img.shields.io/badge/Python-000000?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org/
[Redis]: https://img.shields.io/badge/Redis-000000?style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.io/
