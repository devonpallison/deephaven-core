# The Deephaven R Client

The Deephaven R client is an R package that enables R users to interface with a Deephaven server and perform various
server-side operations from the comfort of RStudio or any other R interface.

## What can the R client do?

The Deephaven Client currently provides three basic functionalities:

1. Connect to a Deephaven server
   -   with anonymous authentication (no username or password)
   -   with basic authentication (username and password)
   -   with custom authentication (general key-value credentials)

2. Interface with Deephaven Tables on the server
   -   Retrieve references to tables on the server
   -   Pull table data into an [Arrow RecordBatchReader](https://arrow.apache.org/docs/r/reference/RecordBatchReader.html),
an [Arrow Table](https://arrow.apache.org/docs/r/reference/Table.html),
a [dplyr Tibble](https://tibble.tidyverse.org),
or an [R Data Frame](https://stat.ethz.ch/R-manual/R-devel/library/base/html/data.frame.html)
   -   Create new tables on the server from an [Arrow RecordBatchReader](https://arrow.apache.org/docs/r/reference/RecordBatchReader.html),
an [Arrow Table](https://arrow.apache.org/docs/r/reference/Table.html),
a [dplyr Tibble](https://tibble.tidyverse.org),
or an [R Data Frame](https://stat.ethz.ch/R-manual/R-devel/library/base/html/data.frame.html)
   -   Bind server-side tables to variable names, enabling access from outside the current R session

3. Run scripts on the server
   -   If the server is equipped with a console, run a script in that console
   -   Currently, Python and Groovy are supported

## Installation

Currently, the R client is only supported on Ubuntu 20.04 or 22.04 and must be built from source.

0. We need a working installation of R on the machine where the R client will be built.
   The R client requires R 4.1.2 or newer; you can install R from the standard packages
   made available by Ubuntu 22.04.  If you want a newer R version or if you are running in
   Ubuntu 20.04, you should install R from CRAN:

   ```
   # Download the key and install it
   $ wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | \
       sudo gpg --dearmor -o /usr/share/keyrings/r-project.gpg

   # Add the R source list to apt's sources list
   $ echo "deb [signed-by=/usr/share/keyrings/r-project.gpg] https://cloud.r-project.org/bin/linux/ubuntu jammy-cran40/" | \
       sudo tee -a /etc/apt/sources.list.d/r-project.list

   # update the apt package list
   $ apt update

   # install R
   $ sudo apt install r-base r-recommended
   ```

1. Build the cpp-client (and any dependent libraries) according to the instructions in
   https://github.com/deephaven/deephaven-core/blob/main/cpp-client/README.md.
   Follow the instructions at least to the point for "Build and install Deephaven C++ client".
   At that point you would have both the Deephaven C++ client and any C++ libraries it depends on,
   all installed in a particular directory of your choosing.
   Define an environment variable `DHCPP` and assign it an absolute path to that directory.

2. Choose a directory where the Deephaven R client source code will live.
   Here, the source code will be downloaded into a new directory called `rdeephaven`.
   Navigate into that directory and clone this subdirectory of `deephaven-core` using git's sparse-checkout:
   ```bash
   mkdir rdeephaven
   cd rdeephaven
   git init
   git remote add -f origin https://github.com/deephaven/deephaven-core.git
   git config core.sparseCheckout true
   echo "R/rdeephaven" >> .git/info/sparse-checkout
   git pull origin main
   ```

3. Start an R console inside the rdeephaven directory, using some environment variable definitions
   to speed up compilation.  Use these commands:
   ```bash
   export NCPUS=`getconf _NPROCESSORS_ONLN`
   export MAKEFLAGS="-j$NCPUS"
   R
   ```
   In that console, install the dephaven client dependencies (since we are building from source
   dependencies will not be automatically pulled in):
   ```r
   install.packages(c('Rcpp', 'arrow', 'R6', 'dplyr'))
   ```
   then install the deephaven client itself:
   ```r
   install.packages(".", repos=NULL, type="source")
   ```
   This last command can also be executed from RStudio without the need for explicitly starting an R console.

4. Now, run
   ```r
   library(rdeephaven)
   ```
   in the R session, and start using the client!

---
**NOTE**

If an error like this occurs in step 3:
```bash
client.cpp:7:10: fatal error: deephaven/client/client.h: No such file or directory
 7 | #include "deephaven/client/client.h"
   |          ^~~~~~~~~~~~~~~~~~~~~~~~~~~
compilation terminated.
```
this means that the C++ compiler does not know where to find the relevant header files for the Deephaven C++ client. This can happen for a handul of reasons:
1. Step 1 was skipped, and the Deephaven C++ client was not installed. In this case, please ensure that the client is installed before attempting to build the R client.
2. The Deephaven C++ client is installed, but the `DHCPP` environment variable is not set. To test this, run
   ```bash
   echo $DHCPP
   ```
   If this returns an empty string, set `DHCPP` according to the instructions in step 1 with
   ```bash
   export DHCPP=/path/to/dhcpp
   ```
3. The Deephaven C++ client is installed and the `DHCPP` environment variable is set, but the current project is not configured to allow the compiler to access the Deephaven `dhcpp` and `src` directories. This is more difficult to give advice on, as it is an IDE-dependent problem. Consult your IDE's documentation on C/C++ compiler include paths for more information.
---

## Running the unit tests

The Deephaven R client utilizes R's `testthat` package to perform unit tests. In order to run these unit tests, install `testthat` via `install.packages("testthat")`. Then, from an R session with `rdeephaven` installed, run the unit tests:
```r
library(testthat)
test_package("rdeephaven")
```

## Debugging

Because the Deephaven R client is written in C++ and wrapped with `Rcpp`, standard R-level debugging is not sufficient for many kinds of problems associated with C++ code. For this reason, debugging the R client must be done with a C++ debugger. We recommend using [Valgrind](https://valgrind.org) to check for memory bugs, and using [gdb](https://www.sourceware.org/gdb/) for thorough backtraces and general debugging.

### Running R with Valgrind

The following was taken from [this blog post](https://kevinushey.github.io/blog/2015/04/05/debugging-with-valgrind/), which has proven very useful for getting started with Valgrind.
1. Install Valgrind with `sudo apt-get install valgrind` or `sudo yum install valgrind`
2. Run R under Valgrind with `R -d valgrind`
   
OS-dependent problems may come up in either step, and the simplest solution is to use a Linux machine or VM if one is available. Attempting these steps in a Linux Docker image may also prove difficult, and will certainly fail if the host architecture is not AMD/X86.

### Running R with gdb

[This article](https://www.maths.ed.ac.uk/~swood34/RCdebug/RCdebug.html) is a good resource for running R with gdb, and also touches on Valgrind use. There are several ways to run R with gdb, and here we only outline the text-based approach given near the bottom of the page.
1. Install gdb with `sudo apt-get install gdb` or `sudo yum install gdb`
2. Start gdb with R attached with `R -d gdb`. This will start a gdb session denoted by `(gdb)` in the console.
3. In the gdb session, start an R console with `(gdb) run`

Both Valgrind and gdb debugging is done through a console, and is not interactive from an IDE. There may be a way to make RStudio play well with Valgrind or gdb, but that is beyond the scope of these instructions.

### Enabling DEBUG level logging for gRPC and the C++ layer of the Deephaven R client

The C++ component of the Deephaven R client uses the C++ implementation of gRPC to exchange messages with a Deephaven server.
gRPC has an internal logging component that can be configured to log to stderr detail information about connection state and messages
exchanged between client and server; the Deephaven R client also uses the same logging component to show client state information.
This can be useful for debugging purposes.  To enable detailed logging, set the environment variable `GRPC_VERVOSITY=DEBUG`

## Code Styling

The Deephaven R client uses the [Tidyverse styleguide](https://style.tidyverse.org) for code formatting, and implements this style with the `styler` package. For contributions, ensure that code is properly styled according to Tidyverse standards by running the following code in your R console, where `/path/to/rdeephaven` is the path to the root directory of this package.
```
setwd("/path/to/rdeephaven")
install.packages("styler")
library(styler)
style_pkg()
```
   
## High-level design overview

The R client uses the
[Deephaven C++ client](https://github.com/deephaven/deephaven-core/tree/main/cpp-client)
as the backend for connecting to and communicating with the server. Any Deephaven-specific feature in the R client is,
at some level, an API for an equivalent feature in the C++ client. 
To make Deephaven's C++ client API available in R, an R6 class provides an R interface to 
[Rcpp](https://github.com/RcppCore/Rcpp) wrapped parts of the C++ API.  Deephaven's C++ API can create Arrow tables, and R has an [Arrow library](https://github.com/apache/arrow/tree/main/r).  Because Arrow is an in-memory data format, Arrow data can be transferred between R and C++ simply by passing a pointer between the languages and using the
[Arrow C Stream Interface](https://arrow.apache.org/docs/format/CStreamInterface.html).  No data copies are required.  
