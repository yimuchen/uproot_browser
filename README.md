# Uproot Browser

A simple utility application for quickly browsing the contents of a root file
to get the general distribution of branches.

While the introduction of [`uproot`][uproot] and [`awkward`][awkward] has
generally made writing analysis code much simpler compared with simply using
[`ROOT`][root], one tool that I did miss was the [`TBrowser`][tbrowser]. In
general, I wanted some way of opening a file a quickly searching if a field
existing, and if it does, check if the distribution looks "nominal". The
creation of this tool was largely inspired by [`fzf`][fzf] and other fuzzy
finding tools. While I debated whether to create this tool as a "plugin" for
`fzf`, I ended up going with a pure python approach, as the physics community
are more familiar with setting up python environment. Also, most analysis
environments typically use a single language environment, meaning that not
everyone will be install the [`go`][go]-based `fzf`. Having everything be a
python-based TUI also means that it *should* on most terminals applications
that physicists are using.

## Installation

Installing this through pip should be as simple as

```bash
python -m pip install git+https://github.com/yimuchen/uproot_browser.git
```

Once installed you can run this module directly with the command

```bash
python -m uproot_browser
```

Here you should be created with TUI column with the handful of shortcuts in the
bottom column.

## A simple demo


https://github.com/user-attachments/assets/7e5d37e9-b4c0-483b-b917-5c6dbd59012d

A quick demo of this program running on CMS open data! Also available [here.](example/example.webm) 

## Road map to 1.0

Right now, the package is open to get gauge the general community interest in
such a tool, as not everyone may care about TUI tools in general. In the future
I hope to add at least the following features before a 1.0:

- Stream line the process for opening files and arrays. This includes but is
  not limited to:
  - Having path auto-completion for files
  - Auto-detect paths to TTree objects in the requested file
  - Avoid the interface hanging when opening files
- Have support for more reading methods: I've currently only tested this
  reading a local ROOT file, as `xrdfs` is commonly used for analysis `ROOT`
  file, reading over the internet would be something I want to be possible for
  the user.
- Support more input formats: `ROOT` was the most commonly used format, but
  there has be a shift of using other formats recently.
- Improving fuzzy finding correct and performance, right now the performance is
  atrocious due to very large rewrites of the displayed list.
- Testing on alternate screen/terminal sizes (and showing error messages when
  it displays cannot be normally introduced)
- Some array modifications. My current target is that if your variable can be
  written as an awkward array one-liner, you should be able to plot it.
- Some plot toggles: getting log-scale axis and such.
- Better documentation

### What will most likely never be added:

- "General" plotting: this tool is not, and will never be, a general analysis
  tool kit. The ensures that the scope of the project remains small and
  discourages physicists from abusing tools. Anything that is comparing 2
  arrays or anything that takes more than a single file (whether that is
  scatter plots or stacked histograms or such) are deemed out of scope.
- Multi-file support: again, this tools should never be used as a general
  analysis tool.
- A "save" button: I don't think the output of generalized scripting
  applications such as this should ever be used for presentation purposes. The
  generation of single arrays should be enough for get you get decent plots
  with external tools.

[awkward]: https://awkward-array.org/doc/main/
[fzf]: https://github.com/junegunn/fzf
[go]: https://go.dev/
[root]: https://root.cern/
[tbrowser]: https://root.cern.ch/doc/master/classTBrowser.html
[uproot]: https://uproot.readthedocs.io/en/stable/basic.html
