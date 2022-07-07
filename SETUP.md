Setup
=====

To get the artifact, run:

```
git clone https://github.com/StefanosChaliasos/solidity-inline-assembly
# Enter the artifact directory.
cd solidity-inline-assembly
```

The easiest (fastest) way to get all dependencies needed for evaluating the artifact 
(i.e., command-line tools and python dependencies) is to download a pre-built 
Docker image from DockerHub. Another option is to build the Docker image locally 
or to install all dependencies on your machine 
(we have only tested this on MacOSX and Ubuntu, but it should also work 
on any Linux distro or Cygwin (or any similar) on Windows).

## Docker Image

We provide a Dockerfile to build an image based on Ubuntu 18.04 that contains:

* An installation of Python (version 3.9.10). 
* An install of SQLite3.
* Various command-line utilities (i.e., `jq`, `curl`, and `cloc`).
* Python packages for analyzing Solidity files, 
performing HTTP requests,
and plotting figures (i.e., `seaborn`, `pandas`, and `matplotlib`). 

### Pull Docker Image from DockerHub

```bash
docker pull schaliasos/solidity-inline-assembly
# Rename the image to be consistent with our scripts
docker tag schaliasos/solidity-inline-assembly solidity-inline-assembly
```

### Build Docker Image Locally

To build the image (named `solidity-inline-assembly`), run the following 
command (estimated running time: 3-5 minutes, 
depending on your internet connection):

```bash
docker build -t solidity-inline-assembly --no-cache .
```

### Spawn a Docker Container

To create a new Docker container run:

```
docker run -ti --rm \
  -v $(pwd)/database:/home/inline/database \
  -v $(pwd)/figures:/home/inline/figures \
  solidity-inline-assembly
```

Note that we mount two local volumes inside the newly-created container. 
The first volume (`database/`) contains the database for performing the
quantitative analysis. The second volume (`figures/`) will be used to save
the figures of our paper.

## Local Installation

### Dependencies

__NOTE:__ It is highly recommended to use virtualenv for python.

You need to download the following software packages:

* Python version 3.9.10.
* The following python packages:

```
requests py-etherscan-api solidity_parser matplotlib seaborn beautifulsoup4 tqdm UpSetPlot
```

* An installation of SQLite3
* The following system packages (the names here are provided as given in the 
APT repository of Ubuntu).

```
curl sqlite3 jq cloc
```
