# My Portfolio

This is a small sampling of my (Dan's) work.

There are a few projects I've developed that I've included
in the portfolio.

## Forks

Inside of the [forks](./forks/readme.md) directory are two
of the forks I've made. One is for
[`sdorfehs`](./forks/sdorfehs/README.md), an X11 window
manager I forked to add extra functionality to, and the
other is [`st`](./forks/st/README.md) which I forked to
customize to my liking.

## `config`

Inside of the [`config`](./config) directory is my
custom configuration script. This keeps my configurations
versioned, builds, and installs them. It also allows for a
single generic configuration file to be used to generate
multiple configurartions depending on the host. Note that
this _should_ run when used by anyone that pulls down the
repository (assuming the necessary Perl dependencies are
installed; be careful running it lest you overwrite any of
your own configs).

Also note that, for the purposes of privacy and security,
many (if not **most**) of the configurations I back up with
this script have been removed or altered.

## `delete-comments`

Inside of the
[`delete-comments`](./delete-comments) directory
is a Perl script I developed to remove various commenting
mechanisms from TeX/LaTeX files. Note that the script
depends on many custom libraries which I ***did not***
write. However, the script was developed entirely by me.

Also note that, in the interest of transparency and
security, I have not included the custom libraries on which
this script depends lest I misrepresent this work as my own
or make public code that was never intended to be
public. As such, the script does not function, but I think
it is still a useful showcase of my ability.

## `get-doi-updates`

Inside of the
[`gen-doi-updates`](./gen-doi-updates) directory
is a Python script I developed to update tens of thousands
of DOIs for a company. It uses Crossref's public metadata
retrieval API, parses XML metadata files, and generates bulk
update files to be submitted to Crossref.