<!-- PROJECT LOGO -->
<h1 align="center">Replay Honeypots</h1>
<!-- <div align="center">
  <strong></strong>
</div> -->
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

<!-- [![Build Status][build-shield]][build-url] -->

[![Contributors][contributors-shield]][contributors-url]
[![GNU GPLv3][license-shield]][license-url] [![Stargazers][stars-shield]][stars-url]
[![Overall Stability][stability-shield]][stability-url]
[![Black][black-shield]][black-url]

</div>

<p align="center">
	<img alt="Replay Manager Demo" src="https://raw.githubusercontent.com/wiki/ReplayProject/ReplayHoneypots/images/gifs/general-demo.gif" width="100%">
</p>

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
  Check out our
  <a href="https://github.com/ReplayProject/ReplayHoneypots/graphs/contributors">
    contributors
  </a>:smile:
</div>

<!-- TABLE OF CONTENTS -->

## Table of Contents

-   [Table of Contents](#table-of-contents)
-   [:sparkles: About The Project](#sparkles-about-the-project)
    -   [:computer: Built With](#computer-built-with)
-   [:joystick: Getting Started](#joystick-getting-started)
-   [:dizzy: Usage](#dizzy-usage)
-   [:blue_car: Roadmap](#blue_car-roadmap)
-   [:gift: Contributing](#gift-contributing)
    -   [Ground Rules](#ground-rules)
    -   [General Steps](#general-steps)
-   [License](#license)
-   [Contact](#contact)

<!-- ABOUT THE PROJECT -->

## :sparkles: About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

This project strives to provide a highly configurable, low interaction honeypot and a
system to handle multi-node deployments.

The Replay honeypots are a security tool designed to monitor and collect useful network
information from active deployments. This project began in 2019, and has been growing in
multiple ways ever since. In August 2020, it was made open source! The most notable
components of the system are the:

-   Honeypots
-   Management System
    -   Data Collection / Export Solution
    -   Frontend Analysis
    -   Replay Command Line Interface (CLI)
-   Deployment Strategy

Currently, the project supports **Docker** and **Bare Metal** deployment options,
although Docker is simpler for managing multiple devices and complex setups.

To expedite the analysis of honeypot logs, a web-based management frontend was created
with local authentication using `Node.js`, `Passport.js`, and `Vue.js`. The frontend
provides a way for users to do basic queries to the log database as well as be alerted
of potential attacks, problems, and/or configuration changes of deployed honeypots. The
user may also export data to an external Security Information and Event Management
System **(SIEM)** by utilizing the database's API.

Additionally, progress is being made on an automated deployment and configuration tool
called the ReplayCLI. This is a command line tool that assists in the administration of
honeypots. This tool assumes that the user has set up SSH keys to connect to the system
on which they intend to deploy a honeypot. This tool is primarily used to deploy
honeypots on bare-metal machines.

### :computer: Built With

|  Replay Honeypots  |     Replay Manager     |
| :----------------: | :--------------------: |
|    [TRIO][trio]    |     [VueJS][vuejs]     |
|   [Scapy][scapy]   |  [Tachyons][tachyons]  |
| [CouchDB][couchdb] | [PassportJS][passport] |

<!-- GETTING STARTED -->

## :joystick: Getting Started

To get a local copy up and running follow these guides

| [Install][install] | [Development][development] | [Users][users] |
| :----------------: | :------------------------: | :------------: |


<!-- USAGE EXAMPLES -->

## :dizzy: Usage

Use this space to show useful examples of how a project can be used. Additional
screenshots, code examples and demos work well in this space. You may also link to more
resources.

_For more examples, please refer to the
[Documentation](https://github.com/ReplayProject/ReplayHoneypots/wiki)_

<!-- ROADMAP -->

## :blue_car: Roadmap

See the [open issues](https://github.com/ReplayProject/ReplayHoneypots/issues) and
[projects](https://github.com/ReplayProject/ReplayHoneypots/projects) for a list of
proposed features (and problems we are addressing).

<!-- CONTRIBUTING -->

## :gift: Contributing

First off, thank you for considering contributing to the Replay Honeypots. Contributions
are what make the open source community such an amazing place to be. Any contributions
you make are **greatly appreciated**.

There are many ways to help: documenting use cases, improving the various guides,
finding bugs, adding to the roadmap with ideas and improvements, or, of course, writing
code to enhance the system.

### Ground Rules

Development responsibilities

-   Ensure cross-platform compatibility for every change that's accepted. ARM, Intel,
    Baremetal, Docker Containers, and Ubuntu Linux.
-   Create issues for any major changes and enhancements that you wish to make. Be
    transparent and look for feedback.
-   Run the test suites and `pre-commmit` checks _(see the Development guide for more
    details)_
-   Update guides and readme if changing anything important that is mentioned/explained
-   Mention an issue number with your commits

At this point, you're ready to make your changes! Feel free to ask for help; everyone is
a beginner at first 😸

> If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has
> changed, and that you need to update your branch so it's easier to merge.

### General Steps

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request and explain what is going on

<!-- LICENSE -->

## License

Distributed under the GNU GPLv3 License. See `LICENSE` for more information.

<!-- CONTACT -->

## Contact

Felix Ritscher Montilla -
[Felix.Ritcher@gmail.com](mailto:Felix.Ritcher@gmail.com?subject=ReplayProject%3A)

Seth Parrish - [me@sethp.cc](mailto:me@sethp.cc?subject=ReplayProject%3A)

Project Link:
[https://github.com/ReplayProject/ReplayHoneypots](https://github.com/ReplayProject/ReplayHoneypots)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[issues-url]: https://github.com/ReplayProject/ReplayHoneypots/issues
[issues-shield]:
    https://img.shields.io/github/issues/ReplayProject/ReplayHoneypots.svg?style=flat-square
[build-url]: https://github.com/ReplayProject/ReplayHoneypots/actions/
[build-shield]:
    https://img.shields.io/github/workflow/status/ReplayProject/ReplayHoneypots/pytest/development?style=flat-square
[contributors-url]: https://github.com/ReplayProject/ReplayHoneypots/graphs/contributors
[contributors-shield]:
    https://img.shields.io/github/contributors/ReplayProject/ReplayHoneypots.svg?style=flat-square
[license-url]: https://github.com/ReplayProject/ReplayHoneypots/blob/master/LICENSE
[license-shield]:
    https://img.shields.io/github/license/ReplayProject/ReplayHoneypots.svg?style=flat-square
[stars-url]: https://github.com/ReplayProject/ReplayHoneypots/stargazers
[stars-shield]:
    https://img.shields.io/github/stars/ReplayProject/ReplayHoneypots.svg?style=flat-square
[stability-url]: https://nodejs.org/api/documentation.html#documentation_stability_index
[stability-shield]:
    https://img.shields.io/badge/stability-experimental-orange.svg?style=flat-square
[black-url]: https://github.com/psf/black/blob/master/README.md
[black-shield]:
    https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square
[product-screenshot]: images/screenshot.png

<!--
TODO: Badges
[![Forks][forks-shield]][forks-url]

[forks-url]: https://github.com/othneildrew/
Best-README-Template/network/members
[forks-shield]:
    https://img.shields.io/github/forks/ReplayProject/ReplayHoneypots.svg?style=flat-square
-->

<!-- Guide Links -->

[install]: https://github.com/ReplayProject/ReplayHoneypots/wiki/Guide:-Install
[development]: https://github.com/ReplayProject/ReplayHoneypots/wiki/Guide:-Developers
[users]: https://github.com/ReplayProject/ReplayHoneypots/wiki/Guide:-Users

<!-- Links for the Build With Section -->

[trio]: https://trio.readthedocs.io/en/stable/
[vuejs]: https://vuejs.org/
[scapy]: https://scapy.net/
[tachyons]: https://tachyons.io/
[couchdb]: https://couchdb.apache.org/
[passport]: http://www.passportjs.org/
