**waterverse-sdg-component**

This is the synthetic data generation (SDG) component project for WATERVERSE.

it consists of two projects:

* 'sdg' is a python package that contains the functionality for defining and generating synthetic data  
* wdme\_sdg\_component is a python/fastapi application that exposes the SDG package to WATERVERSE'S WDME.

All code is python and designed to be used with Python3.12+. Each project contains a requirements.txt file detailing required packages.

The SDG project contains sdg.py and associated sensor definitions in a data folder. The testbed.py file provides a functional harness.

The wdme\_sdg\_component contains an api in main.py, using fastapi and provides a CRUD lifecycle for working with synthetic sensors. The api is a wrapper for the sdg package.  
The api provides an openAPI interface through /docs which details all available calls and expected payloads.

The overall concept and operation of the SDG component is explained in this paper: [https://dx.doi.org/10.15131/SHEF.DATA.29921129.V1](https://dx.doi.org/10.15131/SHEF.DATA.29921129.V1) 