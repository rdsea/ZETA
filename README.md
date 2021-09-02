# ZETA Framework
 <img src="https://img.shields.io/github/languages/top/rdsea/zeta" />
<img src="https://img.shields.io/github/issues-raw/rdsea/zeta?color=green" />


**ZETA (ZEro Trust elAsticity)** is an open-source framework that supports zero-trust in the elasticity of edge-cloud microservices. ZETA also provides support for elasticity delegation capabilities between these edge-cloud microservices. 

---

## Table of contents
1. [Introduction](#introduction)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [About the work](#about)
5. [License](#license)

## Introduction <a name="introduction"></a>
ZETA is a distributed framework aims to support zero-trust in the elasticity operations edge-cloud microservices. It is a platform-agnostic framework that can evaluate contextual trust levels. ZETA takes into consideration a high-level view of the platform services that are deployed on cloud. For more details, checkout the wiki page.


## Dependencies <a name="dependencies"></a>
The baseline ZETA requires
* Docker and docker-compose

There are a few additional external dependencies if you want to generate plots and stress test ZETA. They include:
* k6.io
* Jupyter

## Installation <a name="installation"></a>
The installation of ZETA is quite straight-forward. Although you may have to be careful about the providing the correct manifest. 

Steps: 

* Provide the correct `influxDB.conf`configurations and mount it during the runtime.
* _(First Time only)_ Run the init.db when the observed-knowledge component starts up.
* Edit the `trust-computation/trust_config.yaml` values.
* Put your public/private keypair in the authorization service component
* _(Optional)_ Supplement the `gp_regression.py` with your own.
* Run `docker-compose up`

## About the work <a name="about"></a>
ZETA framework is a part of Master's thesis titled "Establishing trust for secure elasticity in edge-cloud microservices__" written by Rohit Raj and supervised by Prof. Hong-Linh Truong and Prof Aurèlien Francillon. If you use this work, please cite the thesis.

* Raj, Rohit. 2021. _Establishing trust for secure elasticity in edge-cloud microservices_. Master's Thesis. _(Submitted to)_ Aalto University, Finland & Eurecom, France

---

### License <a name="license"></a>
ZETA is licensed under the Apache License 2.0