# alignment-training

As part of a job, I needed to train users how to use
various tools to break LaTeX displays, as well as how to
stylistically adhere to a style guide.

The easiest way I could think of doing this was to employ
[MathJax](https://www.mathjax.org/) and to create little
breaking/coding challenges.

I wrote some very simple HTML, CSS, and Javascript and
created series of breaking challenges. I've included a
sample of one of the "challenges" I created here.

## Note

I am neither a web developer, nor a UI/UX designer. I did my
best, but the goal was not to make something beautiful, but
to at least make something accessible and functional.

## Running

Note that, in many cases, you can simply open
[`main.html`](./main.html) from a browser and it will load
everything automatically. Some (such as Firefox) have
security policies in place that do not allow loading
cross-site scripts from any page using the `file://`
protocol. For that reason, I've also added the
[`serve.py`](./serve.py) script which will serve the page
instead. 