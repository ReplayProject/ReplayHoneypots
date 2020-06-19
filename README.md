<!--
*** Thanks for checking out this README Template. If you have a suggestion that would
*** make this better, please fork the repo and create a pull request or simply open
*** an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** ReplayProject, ReplayHoneypots, twitter_handle, email
-->

<!-- PROJECT LOGO -->
<h1 align="center">Replay Honeypots</h1>
<div align="center">
  <strong></strong>
</div>
<div align="center">
  A <code>performant & low interaction</code> honeypot solution
</div>

<br />

<div align="center">

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Issues][issues-shield]][issues-url]
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url] [![Stargazers][stars-shield]][stars-url]
[![Overall Stability][stability-shield]][stability-url]
[![Black][black-shield]][black-url]

</div>

<div align="center">
  <h3>
    <a href="https://github.com/ReplayProject/ReplayHoneypots/wiki">
      Wiki
    </a>
    <span> | </span>
    <a href="https://github.com/ReplayProject/ReplayHoneypots/releases">
      Releases
    </a>
    <span> | </span>
    <a href="https://github.com/ReplayProject/ReplayHoneypots/wiki/contributing">
      Contributing
    </a>
  </h3>
</div>

<div align="center">
  <sub>Sponsored by <a href="https://prahs.com/">PRAHS</a>, built by
  <a href="https://sethp.cc">Seth Parrish</a> and
  <a href="https://github.com/choojs/choo/graphs/contributors">
    contributors
  </a>
</div>

<!-- TABLE OF CONTENTS -->

## Table of Contents

-   [About the Project](#about-the-project)
    -   [Built With](#built-with)
-   [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
-   [Usage](#usage)
-   [Roadmap](#roadmap)
-   [Contributing](#contributing)
-   [License](#license)
-   [Contact](#contact)
-   [Acknowledgements](#acknowledgements)

<!-- ABOUT THE PROJECT -->

## About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

This project strives to create a highly configurable, low interaction honeypot and a
system to manage deployment at scale.

The Replay honeypots are a security tool designed to monitor and collect information
about the networks they are deployed on. This project began in 2019, and since then has
had significant progress made in the different aspects of the system. The most notable
components of the system are:

-   Honeypots
-   Management System
    -   Data Collection / Export
    -   Frontend Analysis
    -   ReplayCLI
-   Deployment Strategy

Currently, the project supports Docker and Baremetal deployment options, although docker
is simpler for managing multiple devices simutaneously.

To expedite the data analysis of our honeypots’ logs, PRA Health Sciences requested we
implement a management frontend. We created a web-based frontend with local
authentication using Passport.js, Node.js and Vue.js. The frontend provides a way for
our users to query our log database as well as be alerted of potential attacks,
problems, and/or configuration changes of our deployed honeypots. The user may also
export our log data to an external SIEM (Security Information and Event Management
System) by utilizing our database API.

Additionally, we have created an automated deployment and configuration tool called the
HoneyCLI. This is a command line tool that utilizes docker to install, uninstall,
configure, start and stop honeypots. This tool assumes that our user has set up SSH keys
to connect to the system which they intend to deploy a honeypot on. Although this tool
uses docker for its deployment, this tool can also be configured to deploy honeypots on
bare-metal machines.

### Built With

-   [TRIO](https://trio.readthedocs.io/en/latest/index.html)
-   [Scapy](https://scapy.readthedocs.io/en/latest/index.html)
-   [CouchDB](https://docs.couchdb.org/en/stable/)

---

-   [VueJS](https://vuejs.org/)
-   [Tachyons](https://tachyons.io/)
-   [PassportJS](http://www.passportjs.org/)

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these steps.

### TODO: Install & Development Guides

<!-- USAGE EXAMPLES -->

## Usage

Use this space to show useful examples of how a project can be used. Additional
screenshots, code examples and demos work well in this space. You may also link to more
resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<!-- ROADMAP -->

## TODO: Roadmap

See the [open issues](https://github.com/ReplayProject/ReplayHoneypots/issues) for a
list of proposed features (and known issues).

<!-- CONTRIBUTING -->

## TODO: Contributing

<!--
Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
-->

<!--
TODO: LICENSE
## License

Distributed under the MIT License. See `LICENSE` for more information.
-->

<!-- CONTACT -->

## Contact

Seth Parrish -
[ParrishSeth@prahs.com](mailto:parrishseth@prahs.com?subject=ReplayProject%3A)

Project Link:
[https://github.com/ReplayProject/ReplayHoneypots](https://github.com/ReplayProject/ReplayHoneypots)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[issues-shield]:
    https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=flat-square
[contributors-url]:
    https://github.com/othneildrew/Best-README-Template/graphs/contributors
[contributors-shield]:
    https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=flat-square
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[forks-shield]:
    https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=flat-square
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[stars-shield]:
    https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=flat-square
[stability-url]: https://nodejs.org/api/documentation.html#documentation_stability_index
[stability-shield]:
    https://img.shields.io/badge/stability-experimental-orange.svg?style=flat-square
[black-url]: https://github.com/psf/black/blob/master/README.md
[black-shield]:
    https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square
[product-screenshot]: images/screenshot.png

<!--
TODO: Badges
License
[![MIT License][license-shield]][license-url]
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=flat-square

Build
https://shields.io/ for a workflow
[![Build Status][build-shield]][build-url]
[build-url]: https://github.com/ReplayProject/ReplayHoneypots/actions/
[build-shield]: https://img.shields.io/badge/stability-experimental-orange.svg?style=flat-square
-->
